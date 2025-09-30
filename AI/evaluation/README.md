# 🧪 KB RAG 시스템 평가 도구 모음

`tests`와 `tools` 폴더를 통합한 종합 평가 및 관리 도구입니다.

## 📁 폴더 구조

```
evaluation/
├── performance_evaluator.py       # 성능 평가 (정량적 메트릭)
├── pipeline_tester.py             # 파이프라인 테스트 (개발용)
├── test_dataset.py                # 테스트 데이터셋 (120개)
├── manage_data.py                 # 데이터 관리 도구
└── README.md                      # 이 파일
```

## 🎯 도구별 역할

### **1. performance_evaluator.py** (성능 평가)
**정량적 RAG 성능 평가 도구**

#### **특징:**
- 정확한 메트릭: MRR, MAP, NDCG, Precision@K, Recall@K, F1@K
- 답변 품질 평가: 의미적 유사도, 완전성, 관련성
- 성능 등급: 우수/양호/보통/개선필요
- 엔드포인트 선택: Intent 라우팅 vs 기본 RAG

#### **사용법:**
```bash
# 성능 평가 (대화형 메뉴)
python evaluation/performance_evaluator.py

# 실행 시 선택:
# 1단계: 엔드포인트 선택
#   1. process_with_intent_routing (Intent 라우팅)
#   2. query_rag (기본 RAG)
# 
# 2단계: 테스트 유형 선택
#   1. 빠른 테스트 (4개)
#   2. 기본 테스트 (5개)
#   3. 전체 평가 (120개)
#   4. 카테고리별 평가 (20-50개)
#   5. 난이도별 평가 (30-50개)
#   6. 직접 질의 테스트
```

### **2. pipeline_tester.py** (파이프라인 테스트)
**다양한 파이프라인 비교 및 디버깅 도구**

#### **특징:**
- 다양한 파이프라인: LLM, Intent, RAG, LangGraph
- 응답 시간 측정 및 소스 문서 추적
- 엔드포인트 선택 지원
- 카테고리/난이도 필터링

#### **사용법:**
```bash
# 모든 파이프라인 비교
python evaluation/pipeline_tester.py

# 엔드포인트 선택하여 테스트
python evaluation/pipeline_tester.py --endpoint intent --type all  # Intent 라우팅
python evaluation/pipeline_tester.py --endpoint rag --type all     # 기본 RAG

# 카테고리별 테스트
python evaluation/pipeline_tester.py --category company_products --type langgraph

# 특정 질문으로 테스트
python evaluation/pipeline_tester.py --question "KB 4대연금 신용대출에 대해 알려주세요" --endpoint rag
```

### **3. test_dataset.py** (테스트 데이터)
**KB금융 RAG 시스템 테스트 데이터셋**

#### **특징:**
- 4개 카테고리: 상품, 내규, 법률, FAQ
- 3단계 난이도: easy, medium, hard  
- 실제 문서 기반: Hugging Face 데이터셋
- Pinecone 메타데이터 구조 반영

#### **사용법:**
```python
from evaluation.test_dataset import dataset, get_dataset_stats

# 통계 확인
stats = get_dataset_stats()
print(f"총 테스트 케이스: {stats['total_cases']}개")

# 카테고리별 테스트 케이스
product_cases = get_test_cases_by_category("company_products")
```

### **4. 🔧 manage_data.py** (데이터 관리)
**벡터 스토어 및 데이터 관리 도구**

#### **특징:**
- 📁 **데이터 업로드**: 폴더/파일 단위 업로드
- 📊 **상태 모니터링**: 벡터 스토어 통계
- 🗑️ **데이터 삭제**: 전체/조건부 삭제
- 🧪 **빠른 테스트**: 시스템 동작 확인

#### **사용법:**
```bash
# 서버 상태 확인
python evaluation/manage_data.py --action status

# 벡터 스토어 통계
python evaluation/manage_data.py --action stats

# 폴더 업로드
python evaluation/manage_data.py --action upload-folder --path "데이터폴더"

# 파일 업로드
python evaluation/manage_data.py --action upload-files --path "file1.pdf,file2.pdf"

# 빠른 테스트
python evaluation/manage_data.py --action test

# 모든 벡터 삭제 (주의!)
python evaluation/manage_data.py --action delete-all

# 조건부 삭제
python evaluation/manage_data.py --action delete-condition --field main_category --value 상품
```

## 🎯 사용 시나리오

### **개발 단계별 사용법**

#### **1. 일일 개발 중**
```bash
# 새 기능 빠른 검증
python evaluation/rag_flow_checker.py --question "테스트 질문" --type langgraph
```

#### **2. 주간 성능 체크**
```bash
# 파이프라인 간 비교
python evaluation/rag_flow_checker.py --type all
```

#### **3. 월간 정량 평가**
```bash
# 정확한 성능 메트릭
python evaluation/comprehensive_rag_evaluator.py
# 메뉴에서 3번 선택 (종합 평가)
```

#### **4. 릴리즈 전 검증**
```bash
# 1. 데이터 상태 확인
python evaluation/manage_data.py --action stats

# 2. 종합 성능 평가
python evaluation/comprehensive_rag_evaluator.py

# 3. 모든 파이프라인 검증
python evaluation/rag_flow_checker.py --type all
```

## 📊 출력 예시

### **comprehensive_rag_evaluator.py 출력:**
```
🧪 RAG 시스템 종합 평가 도구
==================================================
🔗 테스트할 엔드포인트를 선택하세요:
1. process_with_intent_routing (Intent 라우팅)
2. query_rag (기본 RAG)
==================================================
엔드포인트 선택 (1-2): 1
✅ 선택된 엔드포인트: process_with_intent_routing

📂 선택된 카테고리: company_products
📊 총 50개 테스트 케이스 평가 시작
🔗 사용 엔드포인트: /process_with_intent_routing (intent)
------------------------------------------------------------

🏆 종합 RAG 성능 평가 결과
================================================================================
📈 전체 통계:
  ✅ 성공한 테스트: 45/50 (90.0%)

🔍 문서 검색 성능:
  🎯 Precision@3: 0.850
  🔍 Recall@3: 0.720
  📊 F1@3: 0.780
  🏆 MRR: 0.890
  🗺️  MAP: 0.760
  📈 NDCG@3: 0.820

💬 답변 생성 품질:
  🧠 의미적 유사도: 0.750
  📋 완전성: 0.680
  🎯 관련성: 0.810
  💯 종합 점수: 0.745

🏅 종합 성능 등급:
  📊 종합 점수: 0.785
  🏆 등급: 🥈 양호 (Good)
  💡 권장사항: 좋은 성능입니다. 세부적인 튜닝으로 더 개선할 수 있습니다.
```

### **rag_flow_checker.py 출력:**
```
📝 테스트 1/3: KB 4대연금 신용대출에 대해 알려주세요
----------------------------------------
🚀 RAG 테스트 (intent)
🔗 엔드포인트: /process_with_intent_routing
질문: KB 4대연금 신용대출에 대해 알려주세요

✅ 응답 시간: 1.1초
📂 분류된 카테고리: company_products
소스 문서: 4개
답변: KB 4대연금 신용대출은 4대연금 수령자를 대상으로 하는 신용대출 상품으로...
💡 Intent 분류 → 상품명 추출 → 스마트 검색 (파일명 → 키워드 → 폴더)

📄 소스 문서 상세:
  1. 파일명: KB_4대연금_신용대출.pdf
     카테고리: 상품/개인 신용대출
     청크: 2, 페이지: 1

🧪 LangGraph RAG 테스트 (실험용)
🔗 엔드포인트: /experimental/langgraph_rag
질문: KB 4대연금 신용대출에 대해 알려주세요

🔬 워크플로우 타입: langgraph
📂 분류된 카테고리: company_products
✅ 응답 시간: 1.23초
💡 그래프 기반 노드 실행: classify_intent → search_documents → filter_relevance → generate_response
```

## 🔧 설정 및 환경

### **필수 사항:**
```bash
# 서버 실행
python run_server.py

# 의존성 설치
pip install -r requirements.txt
```

### **환경 변수:**
- `BASE_URL`: API 서버 주소 (기본: http://localhost:8000/api/v1)
- `REQUEST_TIMEOUT`: 요청 타임아웃 (기본: 30초)

## 🚨 주의사항

### **데이터 삭제 시:**
```bash
# 매우 주의! 모든 데이터가 삭제됩니다
python evaluation/manage_data.py --action delete-all
# 'DELETE'를 정확히 입력해야 실행됨
```

### **성능 테스트 시:**
- 서버가 실행 중인지 확인
- 벡터 스토어에 데이터가 있는지 확인
- 네트워크 상태 양호한지 확인

## 💡 팁

### **1. 결과 저장 및 비교**
```bash
# 결과를 JSON으로 저장
python evaluation/rag_flow_checker.py --save langgraph_results.json --type langgraph

# 저장된 결과 확인
cat langgraph_results.json | jq '.[] | {question: .question, response_time: .result.response_time}'
```

### **2. 배치 테스트**
```bash
# 질문 파일 생성
echo "KB 4대연금 신용대출 금리는?" > questions.txt
echo "대출 한도는 얼마까지?" >> questions.txt

# 배치 실행
python evaluation/rag_flow_checker.py --file questions.txt --type all
```

### **3. 성능 모니터링**
```bash
# 정기적인 성능 체크 스크립트
#!/bin/bash
echo "$(date): 성능 체크 시작" >> performance.log
python evaluation/comprehensive_rag_evaluator.py >> performance.log 2>&1
echo "$(date): 성능 체크 완료" >> performance.log
```

---

**💡 통합된 evaluation 폴더로 더 효율적인 RAG 시스템 관리가 가능합니다!**
