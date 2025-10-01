# src/rag/document_loader.py
from typing import List, Dict, Any, Optional
from pathlib import Path
import os, io, uuid, datetime, re
import pandas as pd
from tqdm import tqdm
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import UploadFile
import pdfplumber
import logging

# PDF 폰트 경고 메시지 제거
logging.getLogger("pdfminer.pdffont").setLevel(logging.ERROR)

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.constants import (
    # 카테고리/라벨
    MAIN_LAW, MAIN_RULE, MAIN_PRODUCT,
    SUB_COMMON, SUB_RULE_BANK,
    SUB_PRODUCT_MORTGAGE, SUB_PRODUCT_PERSONAL, SUB_PRODUCT_AUTO,
    SUB_PRODUCT_HOUSING_FUND, SUB_PRODUCT_CORP,
    normalize_sub_label,
    # 키워드
    KEYWORDS_INTEREST_RATE, KEYWORDS_CONDITIONS, KEYWORDS_APPLICATION,
    KEYWORDS_POLICY, KEYWORDS_ETHICS,
    # 파일 관련
    ALLOWED_EXTENSIONS, PDF_EXT, CSV_EXT,
    DATA_FOLDER_NAME,
    # 텍스트 스플리터
    TEXT_SPLITTER_SEPARATORS,
)

from src.constants import (
    # 메타데이터 - 문서 카테고리
    METADATA_DOCUMENT_CATEGORY_REGULATION, METADATA_DOCUMENT_CATEGORY_PRODUCT, METADATA_DOCUMENT_CATEGORY_UPLOADED,
    # 메타데이터 - 서브카테고리
    METADATA_SUBCATEGORY_LAW, METADATA_SUBCATEGORY_CREDIT_POLICY, METADATA_SUBCATEGORY_BANKING_PRODUCT, METADATA_SUBCATEGORY_USER_UPLOAD,
    # 메타데이터 - 비즈니스 유닛
    METADATA_BUSINESS_UNIT_COMPLIANCE, METADATA_BUSINESS_UNIT_CREDIT, METADATA_BUSINESS_UNIT_RETAIL_BANKING, METADATA_BUSINESS_UNIT_GENERAL,
    # 메타데이터 - 상품 타입
    METADATA_PRODUCT_TYPE_MORTGAGE, METADATA_PRODUCT_TYPE_PERSONAL_LOAN, METADATA_PRODUCT_TYPE_AUTO_LOAN,
    METADATA_PRODUCT_TYPE_HOUSING_FUND, METADATA_PRODUCT_TYPE_BUSINESS_LOAN,
    # 메타데이터 - 타겟 고객
    METADATA_TARGET_CUSTOMER_INDIVIDUAL, METADATA_TARGET_CUSTOMER_CORPORATE,
)

# 하위 호환성을 위한 별칭 제거 - constants.py 직접 사용

def _estimate_token_count(text: str) -> int:
    if not text:
        return 0
    return len(text.split())

class DocumentLoader:
    """개선된 문서 로더 - 구조화된 메타데이터 지원"""
    
    def __init__(self):
        # 문서 카테고리 매핑 (폴더명 → 영어 카테고리)
        # 메인 카테고리 표준화(요청 사양 반영)
        self.category_mapping = {
            MAIN_LAW: {
                "document_category": METADATA_DOCUMENT_CATEGORY_REGULATION,
                "subcategory": METADATA_SUBCATEGORY_LAW,
                "business_unit": METADATA_BUSINESS_UNIT_COMPLIANCE,
            },
            MAIN_RULE: {
                "document_category": METADATA_DOCUMENT_CATEGORY_REGULATION,
                "subcategory": METADATA_SUBCATEGORY_CREDIT_POLICY,
                "business_unit": METADATA_BUSINESS_UNIT_CREDIT,
            },
            MAIN_PRODUCT: {
                "document_category": METADATA_DOCUMENT_CATEGORY_PRODUCT,
                "subcategory": METADATA_SUBCATEGORY_BANKING_PRODUCT,
                "business_unit": METADATA_BUSINESS_UNIT_RETAIL_BANKING,
            },
        }
        
        # 상품 유형 매핑
        self.product_mapping = {
            SUB_PRODUCT_MORTGAGE: {"product_type": METADATA_PRODUCT_TYPE_MORTGAGE, "target_customer": METADATA_TARGET_CUSTOMER_INDIVIDUAL},
            SUB_PRODUCT_PERSONAL: {"product_type": METADATA_PRODUCT_TYPE_PERSONAL_LOAN, "target_customer": METADATA_TARGET_CUSTOMER_INDIVIDUAL},
            SUB_PRODUCT_AUTO: {"product_type": METADATA_PRODUCT_TYPE_AUTO_LOAN, "target_customer": METADATA_TARGET_CUSTOMER_INDIVIDUAL},
            SUB_PRODUCT_HOUSING_FUND: {"product_type": METADATA_PRODUCT_TYPE_HOUSING_FUND, "target_customer": METADATA_TARGET_CUSTOMER_INDIVIDUAL},
            SUB_PRODUCT_CORP: {"product_type": METADATA_PRODUCT_TYPE_BUSINESS_LOAN, "target_customer": METADATA_TARGET_CUSTOMER_CORPORATE},
        }

    def _extract_keywords_from_filename(self, filename: str) -> List[str]:
        """파일명에서 키워드 추출"""
        name = Path(filename).stem
        keywords = re.findall(r'[가-힣A-Za-z]+', name)
        return [kw for kw in keywords if len(kw) > 1]

    def _extract_document_info(self, file_path: Path, root_path: Path) -> Dict[str, Any]:
        """파일 경로에서 문서 정보 추출"""
        rel_path = file_path.relative_to(root_path)
        path_parts = rel_path.parts
        
        doc_info = {
            "file_name": file_path.name,
            "file_path": str(rel_path).replace("\\", "/"),
            "file_type": file_path.suffix.lower().lstrip('.'),
            "keywords": self._extract_keywords_from_filename(file_path.name)
        }
        
        # 폴더 구조 정보 추출
        if len(path_parts) >= 1:
            main_category = path_parts[0]
            sub_category = path_parts[1] if len(path_parts) > 1 else ""
            
            # 폴더 정보 추가
            doc_info["main_category"] = main_category
            doc_info["sub_category"] = sub_category
            
            # 메인 카테고리 매핑
            if main_category in self.category_mapping:
                doc_info.update(self.category_mapping[main_category])
            
            # 상품 카테고리인 경우: 서브 라벨 정규화 후 매핑 적용(공백 라벨 기준)
            if main_category == MAIN_PRODUCT:
                normalized = normalize_sub_label(sub_category)
                doc_info["sub_category"] = normalized if normalized else sub_category
                if normalized in self.product_mapping:
                    doc_info.update(self.product_mapping[normalized])
            # 법률/내규 서브 기본값
            if main_category == MAIN_LAW:
                doc_info["sub_category"] = SUB_COMMON
            if main_category == MAIN_RULE and not doc_info.get("sub_category"):
                doc_info["sub_category"] = SUB_RULE_BANK
                
        return doc_info

    def _create_enhanced_metadata(self, base_info: Dict[str, Any], 
                                chunk_idx: int, total_chunks: int,
                                page_num: Optional[int] = None,
                                content: str = "") -> Dict[str, Any]:
        """향상된 메타데이터 생성 - 중복 제거 및 구조 개선"""
        
        # 업로드일 생성 (년-월 형식)
        from datetime import datetime
        upload_date = datetime.now().strftime("%Y-%m")
        
        metadata = {
            # === 핵심 식별 정보 ===
            "file_name": base_info.get("file_name"),
            "file_path": base_info.get("file_path"),
            "file_type": base_info.get("file_type"),
            
            # === 문서 분류 (폴더 구조 기반) ===
            "main_category": base_info.get("main_category"),        # 강령, 법률, 상품 등
            "sub_category": base_info.get("sub_category"),          # 공통, 개인_신용대출 등
            "document_category": base_info.get("document_category"), # policy, product 등
            "subcategory": base_info.get("subcategory"),            # ethics, personal_loan 등
            "business_unit": base_info.get("business_unit"),        # retail_banking 등
            
            # === 청크 정보 ===
            "chunk_index": chunk_idx,
            "content_length": _estimate_token_count(content),
            
            # === 검색 최적화 ===
            "keywords": base_info.get("keywords", []),
            
            # === 상품 관련 (해당하는 경우만) ===
            "product_type": base_info.get("product_type"),
            "target_customer": base_info.get("target_customer"),
            
            # === 업로드 정보 ===
            "upload_date": upload_date,                             # 업로드일 (년-월)
        }
        
        # 페이지 번호 (PDF만)
        if page_num is not None:
            metadata["page_number"] = page_num
            
        # 컨텐츠 기반 스마트 태그
        content_lower = content.lower()
        if any(kw in content_lower for kw in KEYWORDS_INTEREST_RATE):
            metadata["contains_interest_rate"] = True
        if any(kw in content_lower for kw in KEYWORDS_CONDITIONS):
            metadata["contains_conditions"] = True
        if any(kw in content_lower for kw in KEYWORDS_APPLICATION):
            metadata["contains_application_info"] = True
        if any(kw in content_lower for kw in KEYWORDS_POLICY):
            metadata["contains_policy"] = True
        if any(kw in content_lower for kw in KEYWORDS_ETHICS):
            metadata["contains_ethics"] = True
            
        # None 값 제거 (Pinecone 효율성을 위해)
        return {k: v for k, v in metadata.items() if v is not None}

    async def get_document_chunks(self, file: UploadFile) -> List[Document]: # 이걸쓰늕?????????????? 아님 밑???
        """업로드된 파일을 청크로 분할 (향상된 메타데이터 포함)"""
        content_bytes: bytes = await file.read()
        file_name: str = file.filename
        _, file_ext = os.path.splitext(file_name.lower())
        
        # 기본 문서 정보 생성
        base_info = {
            "file_name": file_name,
            "file_path": file_name,
            "file_type": file_ext.lstrip('.'),
            "keywords": self._extract_keywords_from_filename(file_name),
            "document_category": METADATA_DOCUMENT_CATEGORY_UPLOADED,
            "subcategory": METADATA_SUBCATEGORY_USER_UPLOAD,
            "business_unit": METADATA_BUSINESS_UNIT_GENERAL
        }
        
        if file_ext == CSV_EXT:
            return self.get_csv_chunks(content_bytes, base_info)
        elif file_ext == PDF_EXT:
            return self.get_pdf_chunks(content_bytes, base_info)
        raise Exception("Unable to chunk document. Unsupported extension: " + file_ext)

    def get_csv_chunks(self, content_bytes: bytes, base_info: Dict[str, Any]) -> List[Document]:
        """CSV 파일을 청크로 분할"""
        loaded_csv = pd.read_csv(io.BytesIO(content_bytes))
        chunks: List[Document] = []
        total = len(loaded_csv)
        
        for idx, (_, row) in enumerate(tqdm(loaded_csv.iterrows(), total=total)):
            text = row.to_json()
            metadata = self._create_enhanced_metadata(
                base_info, idx, total, content=text
            )
            chunks.append(Document(page_content=text, metadata=metadata))
        return chunks

    def get_pdf_chunks(self, content_bytes: bytes, base_info: Dict[str, Any]) -> List[Document]:
        """PDF 파일을 청크로 분할"""
        chunks: List[Document] = []
        
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            all_texts = []
            page_mapping = []
            
            for page_num, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                    
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=TEXT_SPLITTER_SEPARATORS,
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP
                )
                page_texts = text_splitter.split_text(text)
                all_texts.extend(page_texts)
                page_mapping.extend([page_num] * len(page_texts))
            
            total = len(all_texts)
            for idx, (text_chunk, page_num) in enumerate(zip(all_texts, page_mapping)):
                metadata = self._create_enhanced_metadata(
                    base_info, idx, total, page_num, text_chunk
                )
                chunks.append(Document(page_content=text_chunk, metadata=metadata))
                
        return chunks

    @staticmethod
    def process_folder_and_get_chunks(folder_path: str, allowed_exts: set = ALLOWED_EXTENSIONS) -> List[Document]:
        """폴더의 모든 문서를 처리하여 향상된 메타데이터와 함께 청크 생성"""
        target_folder = Path(folder_path).resolve()
        if not target_folder.exists() or not target_folder.is_dir():
            raise ValueError(f"{folder_path} is not a valid folder")

        # 메타데이터 추출을 위한 root 경로 결정
        # DATA_FOLDER_NAME 내부 구조를 유지하기 위해 부모 경로를 root로 설정
        if DATA_FOLDER_NAME in str(target_folder):
            # DATA_FOLDER_NAME 경로를 찾아서 root로 설정
            parts = target_folder.parts
            data_idx = -1
            for i, part in enumerate(parts):
                if DATA_FOLDER_NAME in part:
                    data_idx = i
                    break
            
            if data_idx >= 0:
                root = Path(*parts[:data_idx+1])
            else:
                root = target_folder.parent
        else:
            root = target_folder.parent

        loader = DocumentLoader()
        all_chunks: List[Document] = []

        for file_path in target_folder.rglob("*"):
            if not file_path.is_file():
                continue
            if allowed_exts and file_path.suffix.lower() not in allowed_exts:
                continue

            try:
                # 파일에서 문서 정보 추출 (올바른 root 경로 사용)
                doc_info = loader._extract_document_info(file_path, root)
                
                # 파일 바이트 읽기
                with open(file_path, "rb") as fh:
                    content_bytes = fh.read()

                # 파일 형식에 따라 처리
                if doc_info["file_type"] == "pdf":
                    chunks = loader.get_pdf_chunks(content_bytes, doc_info)
                elif doc_info["file_type"] == "csv":
                    chunks = loader.get_csv_chunks(content_bytes, doc_info)
                else:
                    continue

                all_chunks.extend(chunks)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return all_chunks


# 모듈 레벨 함수 제거 - DocumentLoader.process_folder_and_get_chunks() 직접 사용 권장