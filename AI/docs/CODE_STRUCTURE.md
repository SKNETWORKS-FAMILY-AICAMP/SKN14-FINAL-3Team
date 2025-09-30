# KB금융 RAG 시스템 코드 구조 가이드

## 📁 프로젝트 전체 구조

```
SKN14-Final-3Team-AI/
├── src/                          # 소스 코드
│   ├── api/                      # FastAPI 엔드포인트
│   │   └── router.py
│   ├── rag/                      # RAG 시스템 핵심
│   │   ├── document_loader.py    # 문서 처리 (메타데이터 생성)
│   │   └── vector_store.py       # 벡터 DB 관리
│   ├── slm/                      # SLM (Structured Language Model)
│   │   ├── slm.py               # SLM 래퍼
│   │   └── langchain.py         # 실험용 (유지)
│   ├── pipelines/               # 파이프라인
│   │   └── sub_main_router.py   # Sub/Main 라우터 기반 파이프라인
│   ├── config.py                # 환경변수 설정
│   ├── constants.py             # 모든 상수 통합
│   ├── main.py                  # FastAPI 앱 진입점
│   └── orchestrator.py          # 기존 워크플로우
├── docs/                        # 문서
└── SKN14-Final-3Team-Data/     # 데이터 폴더
```

## 🏗️ 핵심 모듈 상세 설명

### **1. `src/config.py` - 환경변수 설정**

**역할**: 환경변수와 시스템 설정을 중앙에서 관리

**주요 함수**:
- `get_required_env(key, default)`: 필수 환경변수 가져오기
- `get_required_int_env(key, default)`: 정수형 환경변수 가져오기
- `validate_config()`: 설정값 검증

**설정 항목**:
- `MODEL_KEY`: OpenAI API 키
- `PINECONE_KEY`: Pinecone API 키
- `EMBEDDING_BACKEND`: "openai" 또는 "huggingface"
- `EMBEDDING_MODEL_NAME`: 임베딩 모델명
- `VECTOR_STORE_INDEX_NAME`: Pinecone 인덱스명
- `CHUNK_SIZE`, `CHUNK_OVERLAP`: 문서 청킹 설정

### **2. `src/constants.py` - 상수 통합 관리**

**역할**: 모든 하드코딩된 값들을 상수로 통합 관리

**주요 상수**:
- **메인 카테고리**: `MAIN_LAW`, `MAIN_RULE`, `MAIN_PRODUCT`
- **서브 카테고리**: `SUB_COMMON`, `SUB_RULE_BANK`, 상품 서브 라벨들
- **API 상태**: `STATUS_SUCCESS`, `STATUS_FAIL`
- **FAQ**: `GENERAL_FAQ`
- **메타데이터 키워드**: `KEYWORDS_*` 시리즈
- **파일 확장자**: `ALLOWED_EXTENSIONS`, `PDF_EXT`, `CSV_EXT`
- **로깅 메시지**: `LOG_*` 시리즈
- **검색 파라미터**: `RAG_TOP_K`, `SYNTH_MAX_SNIPPET_CHARS`

**주요 함수**:
- `normalize_sub_label(label)`: 서브 라벨 정규화 (밑줄/공백 혼용 수용)

---

### **3. `src/orchestrator.py` - 기존 워크플로우 조정**

**역할**: 사용자 질의를 분석하고 적절한 처리 방식으로 라우팅

**주요 클래스**:
- `Router`: 질의를 카테고리별로 분류
- `Orchestrator`: 전체 워크플로우 조정

**주요 함수**:
- `run_workflow(prompt)`: 메인 워크플로우 실행
- `query_rag(prompt)`: RAG 시스템으로 질의
- `upload_docs_to_rag(file)`: 문서 업로드
- `upload_folder_to_rag(folder_path)`: 폴더 업로드
- `delete_all_vectors()`: 모든 벡터 삭제
- `delete_vectors_by_condition(field, value)`: 조건부 벡터 삭제

**라우팅 카테고리**:
- `general_banking_FAQs`: 일반 은행 FAQ
- `industry_policies_and_regulations`: 산업 정책/규제
- `company_rules`: 회사 내규
- `company_products`: 회사 상품

---

### **4. `src/pipelines/sub_main_router.py` - 새로운 파이프라인**

**역할**: Sub/Main 라우터 기반의 효율적인 RAG 파이프라인

**주요 함수**:
- `route_sub_category(question)`: 서브 카테고리 라우팅
- `route_main_category(question, sub_category)`: 메인 카테고리 라우팅
- `retrieve_context(question, main_category, sub_category)`: 컨텍스트 검색
- `synthesize_answer(question, main_category, sub_category, docs)`: 답변 합성
- `answer_with_sub_main_router(question)`: 전체 파이프라인 실행

**특징**:
- LLM 기반 라우팅으로 정확한 카테고리 분류
- 메타데이터 기반 효율적인 검색
- 소스 로깅으로 투명한 답변 생성 과정
- GENERAL_FAQ는 LLM 단독으로 빠른 응답

### **5. `src/rag/` - RAG 시스템 핵심**

#### **5.1 `document_loader.py` - 문서 로딩 및 처리**

**역할**: PDF, CSV 등 다양한 문서를 로드하고 청킹

**주요 클래스**:
- `DocumentLoader`: 문서 로딩 및 청킹 처리

**주요 함수**:
- `get_document_chunks(file)`: 단일 파일에서 청크 추출
- `process_folder_and_get_chunks(folder_path)`: 폴더 전체 처리
- `_create_enhanced_metadata()`: 향상된 메타데이터 생성

**메타데이터 생성**:
- 파일 정보: `file_name`, `file_path`, `file_type`
- 폴더 구조: `main_category`, `sub_category`
- 컨텐츠 분석: `keywords`, `contains_ethics`, `contains_policy`
- 업로드 정보: `upload_date`

#### **5.2 `vector_store.py` - 벡터 데이터베이스 관리**

**역할**: Pinecone과의 상호작용 및 벡터 검색

**주요 클래스**:
- `VectorStore`: Pinecone 인덱스 관리

**주요 함수**:
- `get_index_ready()`: 인덱스 준비 및 생성
- `add_documents_to_index(documents)`: 문서를 벡터로 변환하여 추가
- `similarity_search(query, k)`: 유사도 기반 검색
- `similarity_search_by_category(query, category)`: 카테고리별 검색
- `similarity_search_by_folder(query, main_category, sub_category)`: 폴더별 검색
- `delete_documents_by_filter(filter_dict)`: 필터 기반 벡터 삭제 (효율적)
- `delete_vectors_by_condition(field, value)`: 조건부 벡터 삭제 (래퍼)
- `get_index_stats()`: 인덱스 통계 정보

**특징**:
- 배치 처리 (100개씩)로 OpenAI API 토큰 제한 우회
- `delete_documents_by_filter`로 효율적인 벡터 삭제
- 메타데이터 기반 정확한 필터링

---

### **6. `src/api/` - API 엔드포인트**

#### **6.1 `router.py` - FastAPI 라우터**

**역할**: HTTP API 엔드포인트 정의 및 요청 처리

**주요 엔드포인트**:

**기본 기능**:
- `GET /healthcheck`: 서버 상태 확인
- `POST /query_rag`: RAG 질의
- `POST /run_worflow`: 기존 워크플로우 실행
- `POST /run_workflow`: 워크플로우 실행 (별칭)
- `POST /sub_main_answer`: 새로운 Sub/Main 라우터 파이프라인

**데이터 관리**:
- `POST /upload_docs_to_rag`: 개별 파일 업로드
- `POST /ingest_folder`: 폴더 업로드
- `POST /initialize_vector_store`: 전체 데이터 초기화

**데이터 삭제**:
- `DELETE /delete_all_vectors`: 모든 벡터 삭제
- `DELETE /delete_vectors_by_condition`: 조건부 벡터 삭제

**검색 및 상태**:
- `GET /vector_store_status`: 벡터 스토어 상태
- `GET /vector_store_stats`: 벡터 스토어 통계
- `POST /query_rag_by_category`: 카테고리별 검색
- `POST /query_rag_by_folder`: 폴더별 검색

**보안 기능**:
- `_validate_and_resolve_target()`: 경로 검증 및 우회 방지
- `ALLOWED_ROOT` 기준 상대 경로만 허용

---

### **7. `src/slm/` - 구조화된 언어 모델**

**역할**: 질의를 카테고리별로 분류하는 라우터

**주요 기능**:
- `get_structured_output(prompt, response_class)`: 구조화된 출력 생성
- 질의를 4개 카테고리로 자동 분류

---

### **8. `src/slm/langchain.py` - 실험용 LangChain**

**역할**: 실험 및 테스트용 LangChain 구현 (현재 유지)

**주요 기능**:
- 기존 RAG 파이프라인 구현
- 실험적 기능 테스트용

---

### **9. `tools/` - CLI 도구**

#### **9.1 `manage_data.py` - 데이터 관리 CLI**

**역할**: 명령줄에서 데이터 업로드/삭제/상태 확인

**주요 클래스**:
- `DataManager`: 데이터 관리 기능

**주요 함수**:
- `check_server()`: 서버 상태 확인
- `upload_all_data()`: 전체 데이터 업로드
- `upload_folder(folder_name)`: 특정 폴더 업로드
- `upload_file(file_path)`: 개별 파일 업로드
- `delete_vectors_by_condition(field, value)`: 조건부 벡터 삭제
- `get_vector_stats()`: 벡터 스토어 통계

**CLI 명령어**:
- `upload --all`: 전체 데이터 업로드
- `upload --folder [폴더명]`: 특정 폴더 업로드
- `upload --file [파일경로]`: 개별 파일 업로드
- `delete --field [필드명] --value [값]`: 조건부 삭제
- `status`: 시스템 상태 확인
- `clear`: 모든 벡터 삭제

---

### **10. `tests/` - 테스트 코드**

#### **10.1 `comprehensive_rag_evaluator.py` - 통합 테스트 도구**

**역할**: RAG 시스템의 종합적인 성능 평가

**주요 클래스**:

**QuickTester**: 빠른 테스트 (4개 기본 케이스)
- `test_query(prompt, test_name)`: 단일 질의 테스트
- `run_quick_tests()`: 빠른 테스트 실행

**BasicTester**: 기본 테스트 (5개 상세 케이스)
- `test_basic_search(query)`: 기본 검색 테스트
- `analyze_relevance(sources, query)`: 관련성 분석
- `run_basic_tests()`: 기본 테스트 실행

**ComprehensiveRAGEvaluator**: 종합 평가
- `evaluate_single_query(test_case)`: 단일 질의 평가
- `run_comprehensive_evaluation(test_cases, max_tests)`: 종합 평가 실행
- `calculate_aggregate_metrics()`: 전체 지표 집계
- `print_comprehensive_report()`: 종합 보고서 출력

**RAGMetrics**: 검색 성능 지표 계산
- `calculate_precision_at_k()`, `calculate_recall_at_k()`
- `calculate_f1_at_k()`, `calculate_mrr()`, `calculate_map()`
- `calculate_ndcg_at_k()`

**AnswerQualityEvaluator**: 답변 품질 평가
- `calculate_keyword_overlap()`, `calculate_semantic_similarity()`
- `calculate_completeness()`, `calculate_relevance()`

**테스트 옵션**:
1. 🚀 빠른 테스트 (4개 기본 케이스)
2. 🧪 기본 테스트 (5개 상세 케이스)
3. 📊 종합 평가 (데이터셋 기반)
4. 🔍 빠른 질의 테스트 (직접 입력)

#### **10.2 `rag_test_dataset.py` - 테스트 데이터셋**

**역할**: RAG 시스템 테스트를 위한 질의-답변 데이터셋

**데이터 구조**:
- `id`: 테스트 케이스 식별자
- `query`: 질문
- `expected_answer`: 예상 답변
- `expected_file`: 예상 파일명
- `difficulty`: 난이도 (easy/medium/hard)
- `category`: 카테고리 (product/customer_service/compliance/process/emergency)
- `subcategory`: 세부 카테고리

**주요 함수**:
- `get_dataset_stats()`: 데이터셋 통계
- `get_test_cases_by_category(category)`: 카테고리별 테스트 케이스
- `get_test_cases_by_difficulty(difficulty)`: 난이도별 테스트 케이스
- `get_test_cases_by_subcategory(subcategory)`: 세부 카테고리별 테스트 케이스

---

## 🔄 데이터 흐름

### **1. 문서 업로드 과정**
```
사용자 요청 → API 엔드포인트 → DocumentLoader → 청킹 → 메타데이터 생성 → VectorStore → Pinecone
```

### **2. RAG 질의 과정**
```
사용자 질의 → Router → 카테고리 분류 → VectorStore 검색 → 문서 검색 → LLM 답변 생성 → 응답
```

### **3. 조건부 삭제 과정**
```
사용자 요청 → API 엔드포인트 → Orchestrator → VectorStore → 더미 벡터 + 필터 → ID 수집 → 삭제
```

---

## 🎯 주요 설계 패턴

### **1. 데코레이터 패턴**
- `@measure_response_time`: 성능 측정
- `@safe_api_call`: 에러 처리
- `@retry_on_failure`: 재시도 로직

### **2. 전략 패턴**
- `EMBEDDING_BACKEND`에 따른 임베딩 모델 선택
- 다양한 검색 전략 (유사도/카테고리/폴더)

### **3. 팩토리 패턴**
- `DocumentLoader`를 통한 다양한 문서 형식 처리
- `VectorStore`를 통한 벡터 데이터베이스 추상화

### **4. 옵저버 패턴**
- 로깅을 통한 시스템 모니터링
- 백그라운드 작업 진행 상황 추적

---

## 🚀 확장 가능한 구조

### **1. 새로운 문서 형식 추가**
- `DocumentLoader`에 새로운 파서 추가
- `_create_enhanced_metadata()` 함수 확장

### **2. 새로운 검색 전략 추가**
- `VectorStore`에 새로운 검색 메서드 추가
- `Orchestrator`에서 새로운 라우팅 로직 추가

### **3. 새로운 평가 지표 추가**
- `RAGMetrics`에 새로운 지표 계산 함수 추가
- `AnswerQualityEvaluator`에 새로운 품질 측정 방법 추가

### **4. 새로운 API 엔드포인트 추가**
- `router.py`에 새로운 엔드포인트 추가
- 적절한 Pydantic 모델 정의

---

## 📚 추가 학습 자료

- **FastAPI**: https://fastapi.tiangolo.com/
- **Langchain**: https://python.langchain.com/
- **Pinecone**: https://docs.pinecone.io/
- **OpenAI API**: https://platform.openai.com/docs

---

이 문서는 코드 구조를 이해하고 새로운 기능을 추가하거나 기존 코드를 수정할 때 참고하세요! 🎯
