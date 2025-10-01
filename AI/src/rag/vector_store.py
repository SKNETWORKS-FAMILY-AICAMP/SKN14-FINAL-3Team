from typing import List, Literal, Optional, Dict, Any
from uuid import uuid4
import argparse
import logging

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from .document_loader import DocumentLoader

from src.config import PINECONE_KEY, MODEL_KEY, EMBEDDING_MODEL_NAME, EMBEDDING_BACKEND, VECTOR_STORE_INDEX_NAME

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_KEY)
        self.index_name: str = VECTOR_STORE_INDEX_NAME
        # This should be "openai" or "huggingface"
        # Embedding 캐싱 (성능 최적화)
        self._embedding_cache = {}
        self._index_cache = None
        self.embedding_backend: str = EMBEDDING_BACKEND

    def create_index(self) -> None:
        dimension = 1536 if self.embedding_backend == "openai" else 1024
        # This uses the pinecone library
        index = self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
        # 임베딩 모델 정보 출력
        print(f'Created index: {index}')
        print(f'Embedding model: {EMBEDDING_MODEL_NAME} ({self.embedding_backend})')
        print(f'Dimension: {dimension}')

    def check_index_exists(self) -> bool:
        # This uses the pinecone library
        if not self.pc.has_index(self.index_name):
            return False
        return True
    
    def get_index_ready(self) -> None:
        if not self.check_index_exists():
            self.create_index()
    
    def _get_embedding_model(self):
        """embedding_backend 설정에 맞는 embedding model 반환 (성능 최적화)"""
        if self.embedding_backend == "openai":
            return OpenAIEmbeddings(
                model=EMBEDDING_MODEL_NAME,
                api_key=MODEL_KEY,
                chunk_size=500,   # 배치 크기 더 감소 (1000 → 500)
                max_retries=3,    # 재시도 횟수 증가 (1 → 3)
                request_timeout=30, # 타임아웃 증가 (10 → 30)
                retry_min_seconds=1,
                retry_max_seconds=10  # 최대 재시도 간격 증가 (5 → 10)
            )
        elif self.embedding_backend == "huggingface":
            return HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True, "batch_size": 32}  # 배치 크기 최적화
            )
        else:
            raise ValueError(f"Unknown embedding backend: {self.embedding_backend}")

    def get_index(self) -> PineconeVectorStore:
        # This uses the Langchain-pinecone library (캐싱 적용)
        if self._index_cache is None:
            embedding_model = self._get_embedding_model()
            index = self.pc.Index(self.index_name)
            self._index_cache = PineconeVectorStore(index=index, embedding=embedding_model)
        return self._index_cache

    def add_documents_to_index(self, documents: List[Document]) -> List[str]:
        """문서를 인덱스에 추가 (개선된 메타데이터 포함) - 배치 처리"""
        vs_index: PineconeVectorStore = self.get_index()
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        # 메타데이터 정리 - Pinecone에서 지원하지 않는 타입 제거
        cleaned_documents = []
        for doc in documents:
            cleaned_metadata = {}
            for key, value in doc.metadata.items():
                # Pinecone은 string, number, boolean, list of strings만 지원
                if isinstance(value, (str, int, float, bool)):
                    cleaned_metadata[key] = value
                elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                    cleaned_metadata[key] = value
                else:
                    # 복잡한 타입은 문자열로 변환
                    cleaned_metadata[key] = str(value)
            
            cleaned_doc = Document(
                page_content=doc.page_content,
                metadata=cleaned_metadata
            )
            cleaned_documents.append(cleaned_doc)
        
        # 배치 처리 - OpenAI API 토큰 제한 대응 (배치당 50개 문서로 감소)
        batch_size = 50  # 배치 크기 감소 (100 → 50)
        all_ids = []
        
        for i in range(0, len(cleaned_documents), batch_size):
            batch_docs = cleaned_documents[i:i + batch_size]
            batch_ids = uuids[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(cleaned_documents) + batch_size - 1)//batch_size} ({len(batch_docs)} documents)")
            
            try:
                batch_result_ids: List[str] = vs_index.add_documents(documents=batch_docs, ids=batch_ids)
                all_ids.extend(batch_result_ids)
                logger.info(f"Successfully added batch of {len(batch_result_ids)} documents")
            except Exception as e:
                logger.error(f"Failed to add batch starting at index {i}: {e}")
                # 배치가 실패해도 계속 진행
                continue
        
        logger.info(f"Added {len(all_ids)} documents to index (total attempted: {len(documents)})")
        return all_ids
    
    def similarity_search(self, query: str, k: int = 5, 
                         filter_dict: Optional[Dict[str, Any]] = None) -> List[Document]:
        """향상된 유사도 검색 - 메타데이터 필터링 지원 (성능 최적화)"""
        vs_index: PineconeVectorStore = self.get_index()
        
        try:
            if filter_dict:
                # Pinecone 필터 정리 (잘못된 필터 제거)
                clean_filter = {}
                for key, value in filter_dict.items():
                    if isinstance(value, (str, int, float, bool)):
                        clean_filter[key] = value
                    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                        clean_filter[key] = value
                
                if clean_filter:
                    results = vs_index.similarity_search(query, k=k, filter=clean_filter)
                else:
                    results = vs_index.similarity_search(query, k=k)
            else:
                results = vs_index.similarity_search(query, k=k)
        except Exception as e:
            logger.warning(f"Filter search failed, using simple search: {e}")
            # 필터 검색 실패 시 단순 검색으로 fallback
            results = vs_index.similarity_search(query, k=k)
        
        return results

    def similarity_search_by_category(self, query: str, category: str, k: int = 5) -> List[Document]:
        """카테고리별 검색"""
        filter_dict = {"document_category": category}
        return self.similarity_search(query, k=k, filter_dict=filter_dict)


    def similarity_search_by_folder(self, query: str, main_category: str, sub_category: str = None, k: int = 5) -> List[Document]:
        """폴더 구조 기반 검색"""
        filter_dict = {"main_category": main_category}
        if sub_category:
            filter_dict["sub_category"] = sub_category
        return self.similarity_search(query, k=k, filter_dict=filter_dict)

    def similarity_search_by_filename(self, query: str, file_name: str, k: int = 5) -> List[Document]:
        """파일명 기반 검색 (정확 매칭)"""
        filter_dict = {"file_name": file_name}
        return self.similarity_search(query, k=k, filter_dict=filter_dict)

    def similarity_search_by_keywords(self, query: str, keywords: List[str], k: int = 5) -> List[Document]:
        """키워드 기반 검색 - 쿼리에 키워드를 추가하여 검색"""
        try:
            # 키워드를 쿼리에 추가
            enhanced_query = f"{query} {' '.join(keywords)}"
            return self.similarity_search(enhanced_query, k=k)
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """인덱스 통계 정보 조회"""
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            
            # namespaces를 안전하게 처리
            namespaces = stats.get("namespaces", {})
            if namespaces:
                # namespaces의 값들을 JSON 직렬화 가능한 형태로 변환
                safe_namespaces = {}
                for ns_name, ns_data in namespaces.items():
                    if hasattr(ns_data, '__dict__'):
                        safe_namespaces[ns_name] = dict(ns_data)
                    else:
                        safe_namespaces[ns_name] = ns_data
            else:
                safe_namespaces = {}
            
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "namespaces": safe_namespaces
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {
                "total_vectors": 0,
                "dimension": 0,
                "index_fullness": 0,
                "namespaces": {},
                "error": str(e)
            }

    def get_all_unique_metadata(self) -> Dict[str, Any]:
        """벡터 스토어의 모든 고유 메타데이터 값들 조회"""
        try:
            index = self.pc.Index(self.index_name)
            
            # 모든 벡터의 메타데이터 수집
            query_response = index.query(
                vector=[0.0] * (1536 if self.embedding_backend == "openai" else 1024),
                top_k=10000,
                include_metadata=True
            )
            
            unique_values = {
                "file_names": set(),
                "main_categories": set(),
                "sub_categories": set(),
                "file_paths": set()
            }
            
            for match in query_response.matches:
                if match.metadata:
                    if 'file_name' in match.metadata:
                        unique_values["file_names"].add(match.metadata['file_name'])
                    if 'main_category' in match.metadata:
                        unique_values["main_categories"].add(match.metadata['main_category'])
                    if 'sub_category' in match.metadata:
                        unique_values["sub_categories"].add(match.metadata['sub_category'])
                    if 'file_path' in match.metadata:
                        unique_values["file_paths"].add(match.metadata['file_path'])
            
            # set을 list로 변환하여 정렬
            return {
                "file_names": sorted(list(unique_values["file_names"])),
                "main_categories": sorted(list(unique_values["main_categories"])),
                "sub_categories": sorted(list(unique_values["sub_categories"])),
                "file_paths": sorted(list(unique_values["file_paths"])),
                "total_documents": len(query_response.matches)
            }
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {"error": str(e)}

    def delete_documents_by_filter(self, filter_dict: Dict[str, Any]) -> None:
        """필터 조건에 맞는 문서들 삭제"""
        try:
            index = self.pc.Index(self.index_name)
            index.delete(filter=filter_dict)
            logger.info(f"Deleted documents with filter: {filter_dict}")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
    
    def delete_vectors_by_condition(self, field: str, value: str) -> int:
        """특정 조건에 맞는 벡터만 삭제 (delete_documents_by_filter 래퍼)"""
        try:
            # 삭제 전 개수 확인을 위해 검색
            query_vector = [0.0] * (1536 if self.embedding_backend == "openai" else 1024)
            index = self.pc.Index(self.index_name)
            results = index.query(
                vector=query_vector,
                filter={field: {"$eq": value}},
                top_k=10000,
                include_metadata=True
            )
            deleted_count = len(results.matches) if results.matches else 0
            
            if deleted_count == 0:
                logger.info(f"No vectors found with {field} = {value}")
                return 0
            
            # 효율적인 필터 기반 삭제 사용
            self.delete_documents_by_filter({field: value})
            logger.info(f"Deleted {deleted_count} vectors with {field} = {value}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete vectors by condition: {e}")
            raise
    

    def delete_all_vectors(self) -> None:
        vs_index: PineconeVectorStore = self.get_index()
        return vs_index.delete(delete_all=True)

    def get_available_files(self) -> List[str]:
        """인덱스에서 사용 가능한 파일명 목록 반환"""
        try:
            index = self.pc.Index(self.index_name)
            # 메타데이터에서 고유한 파일명들을 추출
            query_response = index.query(
                vector=[0.0] * (1536 if self.embedding_backend == "openai" else 1024),
                top_k=10000,  # 충분히 큰 수로 설정
                include_metadata=True
            )
            
            file_names = set()
            for match in query_response.matches:
                metadata = match.metadata or {}
                file_name = metadata.get('file_name')
                if file_name:
                    file_names.add(file_name)
            
            return list(file_names)
        except Exception as e:
            logger.error(f"Failed to get available files: {e}")
            return []