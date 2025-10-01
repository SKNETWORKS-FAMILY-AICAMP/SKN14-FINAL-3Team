# KB금융 RAG 시스템 사용법

## 🚀 빠른 시작

### 1. 서버 실행
```bash
python run_server.py --reload --host 0.0.0.0 --port 8000

python run_server.py --host 0.0.0.0 --port 8001 --reload # <-- django랑 같이 할 때 서버가 8000으로 같으면 안됨

Get-Content app.log -Encoding UTF8 -Wait -Tail 10 # <-- 로그 같이 찍는거 확인 해보기>
```

### 2. 데이터 업로드
```bash
# 서버 상태 확인
python evaluation/manage_data.py --action status

# 특정 폴더 업로드
python evaluation/manage_data.py --action upload-folder --path 법률
python evaluation/manage_data.py --action upload-folder --path 내규
python evaluation/manage_data.py --action upload-folder --path 상품

# 개별 파일 업로드 (쉼표로 구분)
python evaluation/manage_data.py --action upload-files --path "강령/공통/윤리강령.pdf,법률/개인정보보호법.pdf"

# 빠른 테스트
python evaluation/manage_data.py --action test
```

### 3. RAG 질의
```bash
# 기존 파이프라인
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "KB금융그룹의 윤리강령은 무엇인가요?"}'

# 새로운 Intent 기반 라우터 파이프라인 (권장)
curl -X POST "http://localhost:8000/api/v1/answer_with_intent_router" \
  -H "Content-Type: application/json" \
  -d '{"question": "KB금융그룹의 윤리강령은 무엇인가요?"}'

# LLM 전용 답변 (RAG 없이)
curl -X POST "http://localhost:8000/api/v1/answer_with_llm_only" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "안녕하세요"}'
```

## 📊 시스템 상태 확인

```bash
# CLI로 상태 확인
python evaluation/manage_data.py --action status

# 벡터 스토어 통계
python evaluation/manage_data.py --action stats

# API로 상태 확인
curl -X GET "http://localhost:8000/health"                               # 서버 상태
curl -X GET "http://localhost:8000/api/v1/vector_store_stats"            # 벡터 스토어 통계
```

## 🔍 검색 및 질의

### 기본 RAG 질의
```bash
# 기존 파이프라인
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "질문 내용"}'

# 새로운 Intent 기반 라우터 파이프라인 (권장)
curl -X POST "http://localhost:8000/api/v1/answer_with_intent_router" \
  -H "Content-Type: application/json" \
  -d '{"question": "질문 내용"}'
```

### 카테고리별/폴더별 검색
```bash
# 카테고리별 검색
curl -X POST "http://localhost:8000/api/v1/query_rag_by_category" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "질문 내용"}' \
  -G -d "category=강령"

# 폴더별 검색
curl -X POST "http://localhost:8000/api/v1/query_rag_by_folder" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "질문 내용", "main_category": "강령", "sub_category": "공통"}'
```

## 📁 데이터 관리

### 데이터 업로드
```bash
# 서버 상태 확인
python evaluation/manage_data.py --action status

# 벡터 스토어 통계 확인
python evaluation/manage_data.py --action stats

# 특정 폴더 업로드
python evaluation/manage_data.py --action upload-folder --path 내규
python evaluation/manage_data.py --action upload-folder --path 법률
python evaluation/manage_data.py --action upload-folder --path 상품

# 개별 파일 업로드 (쉼표로 구분)
python evaluation/manage_data.py --action upload-files --path "강령/공통/윤리강령.pdf,법률/개인정보보호법.pdf"

# 빠른 테스트
python evaluation/manage_data.py --action test

# API로 개별 파일 업로드
curl -X POST "http://localhost:8000/api/v1/upload_docs_to_rag" \
  -F "files=@강령/공통/윤리강령.pdf"
```

### 데이터 삭제
```bash
# 전체 삭제 (주의!)
python evaluation/manage_data.py --action delete-all

# 조건부 삭제
python evaluation/manage_data.py --action delete-condition --field file_name --value "경제전망보고서(2025.05).pdf"
python evaluation/manage_data.py --action delete-condition --field main_category --value "상품"
python evaluation/manage_data.py --action delete-condition --field sub_category --value "공통"
python evaluation/manage_data.py --action delete-condition --field upload_date --value "2024-01"

# API로 삭제
curl -X DELETE "http://localhost:8000/api/v1/delete_all_vectors"
curl -X DELETE "http://localhost:8000/api/v1/delete_vectors_by_condition" \
  -H "Content-Type: application/json" \
  -d '{"field": "file_name", "value": "경제전망보고서(2025.05).pdf"}'
```

## 🧪 성능 평가

```bash
# 성능 평가 도구 (추천)
python evaluation/performance_evaluator.py

# 옵션 선택:
# 1. 🚀 빠른 테스트 (4개 기본 케이스)
# 2. 🧪 기본 테스트 (5개 상세 케이스)  
# 3. 📊 종합 평가 (데이터셋 기반)
# 4. 🔍 빠른 질의 테스트 (직접 입력)
```

## 📝 예시 질의

```bash
# 윤리 관련
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "KB금융그룹의 핵심 윤리 가치는 무엇인가요?"}'

# 개인정보 보호
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "개인정보 보호를 위한 관리적 조치는 무엇인가요?"}'

# 내부신고
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "내부신고 대상의 예시는 무엇인가요?"}'
```

## 🔍 지원하는 메타데이터 필드

### **기본 식별 정보**
- `file_name`: 파일명 (예: "경제전망보고서(2025.05).pdf")
- `file_path`: 파일 경로 (예: "강령/공통/경제전망보고서(2025.05).pdf")
- `file_type`: 파일 확장자 (예: "pdf", "csv")

### **폴더 구조 정보**
- `main_category`: 메인 카테고리 (예: "강령", "법률", "상품", "약관", "여신내규")
- `sub_category`: 서브 카테고리 (예: "공통", "개인_신용대출", "기업_대출")
- `document_category`: 문서 카테고리 (예: "policy", "product", "regulation")
- `subcategory`: 세부 카테고리 (예: "ethics", "personal_loan", "law")
- `business_unit`: 비즈니스 단위 (예: "corporate", "retail_banking", "compliance")

### **상품 관련 정보**
- `product_type`: 상품 유형 (예: "mortgage", "personal_loan", "auto_loan")
- `target_customer`: 대상 고객 (예: "individual", "corporate")

### **업로드 정보**
- `upload_date`: 업로드일 (예: "2024-01", "2024-02")

### **컨텐츠 기반 태그**
- `contains_ethics`: 윤리 관련 포함 여부 (true/false)
- `contains_policy`: 정책 관련 포함 여부 (true/false)
- `contains_interest_rate`: 금리 정보 포함 여부 (true/false)
- `contains_conditions`: 조건 정보 포함 여부 (true/false)
- `contains_application_info`: 신청 정보 포함 여부 (true/false)

## 🗑️ 데이터 정리 예시

### **특정 파일 삭제**
```bash
# 특정 파일명으로 삭제
python evaluation/manage_data.py --action delete-condition --field file_name --value "경제전망보고서(2025.05).pdf"

# 특정 경로의 파일 삭제
python evaluation/manage_data.py --action delete-condition --field file_path --value "강령/공통/윤리강령.pdf"
```

### **카테고리별 정리**
```bash
# 강령 폴더의 모든 문서 삭제
python evaluation/manage_data.py --action delete-condition --field main_category --value "강령"

# 상품 폴더의 개인 신용대출만 삭제
python evaluation/manage_data.py --action delete-condition --field sub_category --value "개인_신용대출"

# 정책 관련 문서만 삭제
python evaluation/manage_data.py --action delete-condition --field document_category --value "policy"
```

### **업로드일 기준 정리**
```bash
# 2024년 1월에 업로드된 모든 문서 삭제
python evaluation/manage_data.py --action delete-condition --field upload_date --value "2024-01"
```

### **컨텐츠 기반 정리**
```bash
# 윤리 관련 문서만 삭제
python evaluation/manage_data.py --action delete-condition --field contains_ethics --value "true"

# 금리 정보가 포함된 문서만 삭제
python evaluation/manage_data.py --action delete-condition --field contains_interest_rate --value "true"
```

## 🚨 문제 해결

### 서버 연결 오류
- 서버가 실행 중인지 확인: `python run_server.py --reload`
- 포트 8000이 사용 가능한지 확인

### 데이터 업로드 오류
- OpenAI API 키 설정 확인
- Pinecone API 키 설정 확인
- 파일 경로가 올바른지 확인

### 검색 결과 없음
- 데이터가 업로드되었는지 확인: `python evaluation/manage_data.py status`
- 질문이 너무 구체적이지 않은지 확인
- 카테고리별 검색 시도

## 📋 전체 명령어 요약

### **시스템 관리**
```bash
python evaluation/manage_data.py status                    # 상태 확인
curl -X GET "http://localhost:8000/api/v1/healthcheck"    # 서버 상태
curl -X GET "http://localhost:8000/api/v1/vector_store_stats"  # 벡터 스토어 통계
```

### **데이터 업로드**
```bash
python evaluation/manage_data.py --action upload-folder --path 강령      # 특정 폴더 업로드
python evaluation/manage_data.py --action upload-files --path "강령/공통/윤리강령.pdf"  # 개별 파일 업로드
```

### **데이터 삭제**
```bash
python evaluation/manage_data.py --action delete-all                     # 전체 삭제
python evaluation/manage_data.py --action delete-condition --field [필드명] --value [값]  # 조건부 삭제
```

### **RAG 질의**
```bash
# 기존 파이프라인
curl -X POST "http://localhost:8000/api/v1/query_rag" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "질문 내용"}'

# 새로운 Intent 기반 라우터 파이프라인 (권장)
curl -X POST "http://localhost:8000/api/v1/answer_with_intent_router" \
  -H "Content-Type: application/json" \
  -d '{"question": "질문 내용"}'
```

### **성능 평가**
```bash
python evaluation/performance_evaluator.py           # 성능 평가 도구
python evaluation/pipeline_tester.py --type all     # 파이프라인 테스트
python evaluation/pipeline_tester.py --type langgraph    # LangGraph 실험용 테스트
```

## 📚 추가 정보

더 자세한 정보는 `docs/README.md`를 참조하세요.
