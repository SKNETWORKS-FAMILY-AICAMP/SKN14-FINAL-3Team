from typing import List, Any, Dict, Sequence, Union
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from fastapi import UploadFile

from src.slm.slm import SLM
from src.rag.vector_store import VectorStore
from src.rag.document_loader import DocumentLoader
from src.intent_router import IntentRouter
from src.constants import (
    NO_ANSWER_MSG,
    MAIN_LAW, MAIN_RULE, MAIN_PRODUCT,
    GENERAL_FAQ_CATEGORY,
    COMPANY_PRODUCTS_CATEGORY,
    COMPANY_RULES_CATEGORY,
    INDUSTRY_POLICY_CATEGORY,
)

# 상수들은 constants.py에서 import
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT_TEMPLATE = """당신은 KB금융그룹의 내부 문서를 기반으로 답변하는 AI 어시스턴트입니다.

지침:
1) 제공된 <검색된_문서>에 질문과 관련된 정보가 있다면, 그 정보를 바탕으로 정확한 답변을 제공하세요.
2) 검색된 문서에 질문과 관련된 내용이 전혀 없거나 매우 부족하다면, 정확히 "해당 정보를 찾을 수 없습니다"라고 답하세요.
3) 추측하거나 문서에 없는 내용을 만들어내지 마세요.
4) 답변은 한국어로 명확하고 구체적으로 작성하세요.
5) 가능한 경우 문서의 정확한 내용을 인용하여 답변하세요.

<검색된_문서>
{context}
</검색된_문서>
"""

class Orchestrator:
    def __init__(self):
        self.slm = SLM()
        self.vector_store = VectorStore()
        self.router = IntentRouter()

    def answer_with_llm_only(self, prompt: str) -> str:
        """LLM만 사용하는 간단한 답변 (RAG 없이)"""
        response = self.slm.invoke(prompt)
        return response

    def process_with_intent_routing(self, prompt: str) -> Dict[str, Any]:
        """기존 제임스 Intent 분류 후 적절한 처리 방식으로 답변 생성"""
        route_category: str = self.router.route_prompt(prompt)
        print(f"Category: {route_category}")
        if route_category == GENERAL_FAQ_CATEGORY:
            # 일반 FAQ용 시스템 메시지
            general_system_message = SystemMessage("""당신은 KB금융그룹의 고객 상담 전문가입니다.

            지침:
            1) 일반적인 금융 상식이나 KB금융그룹의 기본 정보에 대해 친근하고 정확하게 답변하세요.
            2) 복잡한 금융 용어는 쉽게 풀어서 설명하세요.
            3) 구체적인 상품 정보나 규정이 필요한 경우, "상세한 상담을 위해 KB금융그룹에 직접 문의하시기 바랍니다"라고 안내하세요.
            4) 고객의 상황에 맞는 일반적인 조언을 제공하되, 개인 맞춤 상담은 별도 안내하세요.
            5) 항상 정중하고 도움이 되는 어조로 답변하세요.
            6) 답변은 5줄 이내로 간결하게 작성하세요.""")
            
            prompt_messages = [general_system_message, HumanMessage(prompt)]
            response: str = self.slm.invoke(prompt_messages)
            return {"response": response, "sources": [], "category": route_category}
        elif (  route_category == COMPANY_PRODUCTS_CATEGORY or 
                route_category == COMPANY_RULES_CATEGORY or
                route_category == INDUSTRY_POLICY_CATEGORY
            ):
            # RAG를 사용하는 경우 소스 정보도 함께 반환
            self.vector_store.get_index_ready()
            
            # route_category에 따라 적절한 main_category로 검색
            if route_category == COMPANY_PRODUCTS_CATEGORY:
                main_category = MAIN_PRODUCT
            elif route_category == COMPANY_RULES_CATEGORY:
                main_category = MAIN_RULE
            elif route_category == INDUSTRY_POLICY_CATEGORY:
                main_category = MAIN_LAW
            else:
                main_category = None
            
            # main_category별 검색 또는 일반 검색
            if main_category:
                # 상품 카테고리의 경우 상품명을 추출하여 파일명으로 필터링 시도
                if main_category == MAIN_PRODUCT:
                    product_name = self._extract_product_name_from_question(prompt)
                    print(f"[INTENT] Extracted product name: '{product_name}'")
                    
                    if product_name:
                        # 스마트 상품 검색 시도
                        retrieved_docs: List[Document] = self._smart_product_search(prompt, product_name)
                        # 스마트 검색 실패 시 폴더 검색으로 폴백
                        if not retrieved_docs:
                            retrieved_docs: List[Document] = self.vector_store.similarity_search_by_folder(
                                prompt, main_category
                            )
                            print(f"[INTENT] Fallback to folder search: {len(retrieved_docs)} docs")
                    else:       
                        # 상품명이 추출되지 않은 경우 폴더로 검색
                        retrieved_docs: List[Document] = self.vector_store.similarity_search_by_folder(
                            prompt, main_category
                        )
                        print(f"[INTENT] No product name, folder search: {len(retrieved_docs)} docs")
                else:
                    # 상품이 아닌 경우 폴더로 검색
                    retrieved_docs: List[Document] = self.vector_store.similarity_search_by_folder(
                        prompt, main_category
                    )
            else:
                retrieved_docs: List[Document] = self.vector_store.similarity_search(prompt)
            
            if not retrieved_docs:
                return {"response": "해당 정보를 찾을 수 없습니다.", "sources": [], "category": route_category}
                
            # Document 객체들을 텍스트로 변환
            retrieved_content = []
            sources = []
            for doc in retrieved_docs:
                content = doc.page_content or ""
                metadata = doc.metadata or {}
                file_name = metadata.get('file_name', 'Unknown')
                main_category = metadata.get('main_category', 'Unknown')
                sub_category = metadata.get('sub_category', 'Unknown')
                
                retrieved_content.append(f"[출처: {file_name} ({main_category}/{sub_category})]\n{content}")
                sources.append(dict(metadata))  # 소스 정보 저장
            
            context_text = "\n\n".join(retrieved_content)
            
            # 카테고리별 맞춤 시스템 메시지 생성
            system_message = self._build_category_specific_system_message(route_category, context_text)
            
            prompt_messages: List[SystemMessage, HumanMessage] = []
            prompt_messages.append(system_message)
            prompt_messages.append(HumanMessage(prompt))
            response: str = self.slm.invoke(prompt_messages)
            return {"response": response, "sources": sources, "category": route_category}
        else:
            raise Exception("Router didn't choose a valid category.")

    def query_rag(self, query: str) -> Dict[str, Any]:
        """RAG를 사용하여 쿼리에 응답합니다."""
        self.vector_store.get_index_ready()
        
        # 상품명 추출 시도
        product_name = self._extract_product_name_from_question(query)
        raw_retrieved = []
        
        print(f"[RAG] Extracted product name: '{product_name}'")
        
        if product_name:
            # 1차: 파일명 정확 매칭 시도 (언더스코어 버전)
            filename_with_underscores = product_name.replace(" ", "_") + ".pdf"
            raw_retrieved = self.vector_store.similarity_search_by_filename(query, filename_with_underscores)
            if raw_retrieved:
                print(f"[RAG] Found {len(raw_retrieved)} docs by filename")
            else:
                # 2차: 키워드 검색 시도
                keywords = self._extract_keywords_from_product_name(product_name)
                raw_retrieved = self.vector_store.similarity_search_by_keywords(query, keywords)
                if raw_retrieved:
                    print(f"[RAG] Found {len(raw_retrieved)} docs by keywords")
                else:
                    # 3차: 일반 검색으로 폴백
                    raw_retrieved = self.vector_store.similarity_search(query)
                    print(f"[RAG] Fallback to general search: {len(raw_retrieved)} docs")
        else:
            # 상품명이 추출되지 않은 경우 일반 검색
            raw_retrieved = self.vector_store.similarity_search(query)
            print(f"[RAG] No product name, general search: {len(raw_retrieved)} docs")

        # 검색 결과 정규화 및 스코어 기반 필터링
        retrieved_docs = self._normalize_retrieved(raw_retrieved)
        retrieved_docs = self._filter_by_relevance_score(retrieved_docs, query)

        # 컨텍스트가 비었으면 바로 종료
        if not retrieved_docs:
            return {"response": NO_ANSWER_MSG, "sources": []}

        context_text = self._format_context(retrieved_docs)
        if not context_text.strip():
            return {"response": NO_ANSWER_MSG, "sources": []}
        
        # 검색된 문서의 최소 길이 체크 (너무 짧으면 관련성이 낮을 가능성)
        if len(context_text) < 50:
            return {"response": NO_ANSWER_MSG, "sources": []}

        # LLM 호출 - 개선된 시스템 메시지 사용
        system_message = self._build_enhanced_rag_system_message(context_text)
        prompt = [system_message, HumanMessage(query)]
        try:
            response: str = self.slm.invoke(prompt)
        except Exception:
            response = None

        # 소스 메타데이터 추출
        sources = []
        for d in retrieved_docs:
            meta = dict(d.metadata or {})
            if "relative_path" not in meta:
                rf = meta.get("root_folder")
                fn = meta.get("file_name")
                if rf and fn:
                    meta["relative_path"] = f"{rf}/{fn}"
            sources.append(meta)

        return {
            "response": response or NO_ANSWER_MSG,
            "sources": sources
        }

    def _smart_product_search(self, query: str, product_name: str) -> List[Document]:
        """상품명 기반 스마트 검색 (파일명 → 키워드 → 폴더 순서)"""
        # 1차: 파일명 정확 매칭
        filename_with_underscores = product_name.replace(" ", "_") + ".pdf"
        docs = self.vector_store.similarity_search_by_filename(query, filename_with_underscores)
        if docs:
            print(f"[SEARCH] Found {len(docs)} docs by filename")
            return docs
        
        # 2차: 키워드 검색
        keywords = self._extract_keywords_from_product_name(product_name)
        docs = self.vector_store.similarity_search_by_keywords(query, keywords)
        if docs:
            print(f"[SEARCH] Found {len(docs)} docs by keywords")
            return docs
        
        print(f"[SEARCH] No docs found by filename or keywords")
        return []

    async def upload_docs_to_rag(self, file: UploadFile) -> List[str]:
        """업로드된 파일을 벡터 스토어에 추가합니다."""
        self.vector_store.get_index_ready()
        documents: List[Document] = await DocumentLoader().get_document_chunks(file)
        if not documents:
            return []
        uploaded_ids: List[str] = self.vector_store.add_documents_to_index(documents)
        return uploaded_ids

    def upload_folder_to_rag(self, folder_path: str) -> List[str]:
        """폴더의 모든 문서를 벡터 스토어에 업로드합니다."""
        self.vector_store.get_index_ready()
        documents: List[Document] = DocumentLoader.process_folder_and_get_chunks(folder_path)
        if not documents:
            return []
        uploaded_ids: List[str] = self.vector_store.add_documents_to_index(documents)
        return uploaded_ids

    def delete_all_vectors(self) -> None:
        """벡터 스토어의 모든 벡터를 삭제합니다."""
        if not self.vector_store.check_index_exists():
            raise Exception("Vectors cannot be deleted as index doesn't exist.")
        return self.vector_store.delete_all_vectors()

    def delete_vectors_by_condition(self, field: str, value: str) -> int:
        """특정 조건에 맞는 벡터만 삭제합니다."""
        if not self.vector_store.check_index_exists():
            raise Exception("Vectors cannot be deleted as index doesn't exist.")
        return self.vector_store.delete_vectors_by_condition(field, value)

    def _extract_product_name_from_question(self, question: str) -> str:
        """질문에서 상품명을 추출하는 메서드"""
        from pydantic import BaseModel, Field
        
        class ProductNameResponse(BaseModel):
            product_name: str = Field(
                ...,
                description="질문에서 언급된 KB금융그룹 상품명만 추출하세요. 상품명이 없으면 빈 문자열을 반환하세요."
            )
        
        try:
            # 더 명확한 프롬프트로 상품명만 추출
            extraction_prompt = f"""
                다음 질문에서 KB금융그룹 상품명만 추출하세요. 답변을 생성하지 말고 상품명만 추출하세요.

                질문: {question}

                상품명 예시: KB 동반성장협약 상생대출, KB닥터론, KB 스마트론, KB 햇살론 등
            """
            product_response = self.slm.get_structured_output(
                extraction_prompt,
                ProductNameResponse
            )
            return product_response.product_name.strip()
        except Exception as e:
            print(f"[ERROR] Failed to extract product name: {e}")
            return ""

    def _extract_keywords_from_product_name(self, product_name: str) -> List[str]:
        """상품명에서 핵심 키워드 추출"""
        import re
        
        # 상품명에서 핵심 키워드 추출
        keywords = []
        
        # KB 제거
        clean_name = product_name.replace("KB", "").strip()
        
        # 공백으로 분리하여 키워드 추출
        words = re.findall(r'[가-힣]+', clean_name)
        
        # 의미있는 키워드만 선택 (1글자 제외)
        for word in words:
            if len(word) > 1:
                keywords.append(word)
        
        # 특별한 키워드 매핑
        keyword_mapping = {
            "동반성장협약": ["동반성장", "협약", "상생"],
            "상생대출": ["상생", "대출"],
            "닥터론": ["닥터론"],
            "스마트론": ["스마트론"],
            "햇살론": ["햇살론"]
        }
        
        # 매핑된 키워드 추가
        for key, mapped_keywords in keyword_mapping.items():
            if key in product_name:
                keywords.extend(mapped_keywords)
        
        # 중복 제거
        return list(set(keywords))

    def _normalize_retrieved(self, items: Sequence[Union[Document, str, Dict[str, Any]]]) -> List[Document]:
        """검색 결과를 Document 리스트로 정규화합니다."""
        norm: List[Document] = []
        for it in items or []:
            if isinstance(it, Document):
                norm.append(it)
            elif isinstance(it, str):
                norm.append(Document(page_content=it, metadata={"source_type": "raw_text"}))
            elif isinstance(it, dict):
                text = it.get("page_content") or it.get("text") or it.get("content") or ""
                meta = it.get("metadata") or {}
                norm.append(Document(page_content=text, metadata=meta))
            else:
                norm.append(Document(page_content=str(it), metadata={"source_type": "unknown"}))
        return norm

    def _format_context(self, docs: Sequence[Document]) -> str:
        """Document 리스트를 컨텍스트 문자열로 포맷합니다."""
        lines = []
        for d in docs:
            meta = d.metadata or {}
            src = meta.get("relative_path") or meta.get("file_name") or meta.get("source_type") or "unknown_source"
            snippet = (d.page_content or "").strip()
            if not snippet:
                continue
            lines.append(f"[source: {src}]\n{snippet}")
        return "\n---\n".join(lines)

    def _build_system_message(self, retrieved: Sequence[Union[Document, str]]) -> SystemMessage:
        """검색된 문서들로부터 시스템 메시지를 생성합니다."""
        ctx = self._format_context(retrieved)
        return SystemMessage(_SYSTEM_PROMPT_TEMPLATE.format(context=ctx))
    
    def _build_category_specific_system_message(self, category: str, context_text: str) -> SystemMessage:
        """카테고리별 맞춤 시스템 메시지를 생성합니다."""
        
        if category == COMPANY_PRODUCTS_CATEGORY:
            system_prompt = """당신은 KB금융그룹의 금융상품 전문 상담사입니다.

            지침:
            1) 제공된 <검색된_문서>는 KB금융그룹의 공식 상품 정보입니다.
            2) 상품의 특징, 조건, 금리, 한도, 신청방법 등을 정확하고 구체적으로 안내하세요.
            3) 고객이 이해하기 쉽도록 친근하고 전문적인 어조로 답변하세요.
            4) 상품 비교나 추천이 필요한 경우, 문서 내용을 바탕으로 객관적으로 설명하세요.
            5) 문서에 없는 정보는 "추가 상담이 필요합니다"라고 안내하세요.
            6) 가능한 경우 관련 상품이나 서비스도 함께 안내하세요.
            7) 답변은 5줄 이내로 간결하게 작성하세요.

            <검색된_문서>
            {context}
            </검색된_문서>"""
            
        elif category == COMPANY_RULES_CATEGORY:
            system_prompt = """당신은 KB금융그룹의 내부 규정 및 정책 전문가입니다.

            지침:
            1) 제공된 <검색된_문서>는 KB금융그룹의 공식 내부 규정과 정책입니다.
            2) 규정의 목적, 적용 범위, 세부 조건, 절차 등을 정확하고 명확하게 설명하세요.
            3) 복잡한 규정은 단계별로 나누어 이해하기 쉽게 설명하세요.
            4) 관련 법령이나 상위 규정과의 관계도 함께 설명하세요.
            5) 규정 해석에 애매함이 있을 경우, 가능한 해석을 모두 제시하세요.
            6) 문서에 명시되지 않은 예외사항은 "별도 확인이 필요합니다"라고 안내하세요.
            7) 답변은 5줄 이내로 간결하게 작성하세요.

            <검색된_문서>
            {context}
            </검색된_문서>"""
            
        elif category == INDUSTRY_POLICY_CATEGORY:
            system_prompt = """당신은 금융업계 정책 및 법규 전문가입니다.

            지침:
            1) 제공된 <검색된_문서>는 금융업계 관련 법률, 정책, 규제 정보입니다.
            2) 법령의 목적, 주요 내용, 적용 대상, 시행 시기 등을 체계적으로 설명하세요.
            3) 금융기관에 미치는 영향과 준수해야 할 사항을 구체적으로 안내하세요.
            4) 관련 법령 간의 관계나 개정 사항이 있다면 함께 설명하세요.
            5) 법령 해석이 복잡한 경우, 핵심 포인트를 먼저 제시한 후 세부사항을 설명하세요.
            6) 실무 적용 시 주의사항이나 예외 조건이 있다면 강조하여 안내하세요.
            7) 답변은 5줄 이내로 간결하게 작성하세요.

            <검색된_문서>
            {context}
            </검색된_문서>"""
            
        else:
            # 기본 시스템 메시지 사용
            system_prompt = _SYSTEM_PROMPT_TEMPLATE
        
        return SystemMessage(system_prompt.format(context=context_text))
    
    def _filter_by_relevance_score(self, docs: List[Document], query: str) -> List[Document]:
        """간단한 관련성 기반 필터링 (리랭킹 대신)"""
        if not docs:
            return docs
        
        # 키워드 기반 간단한 스코어링
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in docs:
            content = (doc.page_content or "").lower()
            metadata = doc.metadata or {}
            
            # 기본 점수 (벡터 유사도 이미 반영됨)
            score = 1.0
            
            # 키워드 매칭 보너스
            content_words = set(content.split())
            keyword_overlap = len(query_words.intersection(content_words))
            score += keyword_overlap * 0.1
            
            # 메타데이터 키워드 매칭 보너스
            metadata_keywords = metadata.get("keywords", [])
            for keyword in metadata_keywords:
                if keyword.lower() in query.lower():
                    score += 0.2
            
            # 파일명 매칭 보너스
            file_name = metadata.get("file_name", "").lower()
            for word in query_words:
                if word in file_name:
                    score += 0.3
            
            scored_docs.append((score, doc))
        
        # 점수 순으로 정렬 후 상위 문서만 반환
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # 최소 점수 기준 적용 (너무 관련성이 낮은 문서 제거)
        min_score = 1.0  # 기본 점수 이하는 제거
        filtered_docs = [doc for score, doc in scored_docs if score >= min_score]
        
        print(f"[RELEVANCE] Filtered {len(docs)} → {len(filtered_docs)} docs")
        return filtered_docs[:5]  # 최대 5개만 유지
    
    def _build_enhanced_rag_system_message(self, context_text: str) -> SystemMessage:
        """query_rag용 개선된 시스템 메시지"""
        enhanced_prompt = """당신은 KB금융그룹의 전문 AI 어시스턴트입니다.

        지침:
        1) 제공된 <검색된_문서>는 KB금융그룹의 공식 문서에서 검색된 정보입니다.
        2) 문서 내용을 바탕으로 정확하고 구체적인 답변을 제공하세요.
        3) 상품 정보의 경우: 특징, 조건, 금리, 한도, 신청방법 등을 명확히 안내하세요.
        4) 규정/정책의 경우: 목적, 적용범위, 절차, 주의사항 등을 체계적으로 설명하세요.
        5) 문서에 없는 정보는 추측하지 말고 "문서에서 해당 정보를 찾을 수 없습니다"라고 안내하세요.
        6) 복잡한 내용은 이해하기 쉽게 단계별로 설명하세요.
        7) 답변은 5줄 이내로 간결하게 작성하세요.
        8) 가능한 경우 출처 문서명을 언급하여 신뢰성을 높이세요.

        <검색된_문서>
        {context}
        </검색된_문서>"""
        
        return SystemMessage(enhanced_prompt.format(context=context_text))
    
    # 참고: 하이브리드 서치(Dense + Sparse) 대신 현재 구현된 방식을 사용하는 이유:
    # 1. 메타데이터 기반 필터링으로 정확한 문서 선별 가능
    # 2. 계층적 검색 전략으로 높은 정밀도 확보
    # 3. 도메인 특화된 키워드 매칭으로 충분한 성능
    # 4. 추가 인프라 비용 및 복잡성 불필요
    # 5. 현재 검색 결과 수(k=5)가 작아 하이브리드의 이점 제한적