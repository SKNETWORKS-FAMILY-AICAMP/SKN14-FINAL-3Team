# 🧪 RAG 시스템 테스팅 전략 (통합 버전)

## 📁 evaluation 폴더 구조

```
evaluation/
├── performance_evaluator.py       # 성능 평가 (정량적 메트릭)
├── pipeline_tester.py             # 파이프라인 테스트 (개발용)
├── test_dataset.py                # 테스트 데이터셋 (120개)
├── openai_evaluator.py            # OpenAI 기반 답변 품질 평가
├── manage_data.py                 # 데이터 관리 도구
└── README.md                      # 통합 사용 가이드
```

## 🔧 도구별 역할 분석

### **1. evaluation/performance_evaluator.py** (성능 평가용)

#### **목적**: 정량적 성능 평가 및 벤치마킹
- ✅ **정확한 메트릭**: MRR, MAP, NDCG, Precision@K, Recall@K
- ✅ **120개 테스트 케이스**: 카테고리별/난이도별 세분화
- ✅ **스마트 필터링**: 카테고리별, 난이도별 선택 평가
- ✅ **통계적 분석**: 신뢰할 수 있는 성능 지표

#### **사용 시나리오**:
```bash
# 성능 평가 (대화형 메뉴)
python evaluation/performance_evaluator

# 메뉴 옵션:
# 1. 빠른 테스트 (4개)
# 2. 기본 테스트 (5개) 
# 3. 전체 평가 (120개) ⚠️ 시간 소요
# 4. 📂 카테고리별 평가 (20-50개)
# 5. 📈 난이도별 평가 (30-50개)
# 6. 직접 질의 테스트
```

### **2. evaluation/pipeline_tester.py** (개발/디버깅용)

#### **목적**: 빠른 파이프라인 비교 및 디버깅
- ✅ **다양한 파이프라인 지원**: Intent 라우팅, 기본 RAG, 🧪 LangGraph
- ✅ **대화형 메뉴**: 직관적인 사용자 인터페이스
- ✅ **실시간 디버깅**: 응답 시간, 소스 문서 확인
- ✅ **필터링 지원**: 카테고리별, 난이도별 테스트
- ✅ **OpenAI 평가**: 답변 품질 자동 평가 (선택사항)

#### **사용 시나리오**:
```bash
# 대화형 메뉴 실행
python evaluation/pipeline_tester.py

# 메뉴 옵션:
# 1. 엔드포인트 선택 (Intent/RAG/LangGraph)
# 2. 테스트 유형 선택 (기본/카테고리별/난이도별/직접입력/파일/대량)
# 3. OpenAI 평가 사용 여부 선택
```

### **3. evaluation/manage_data.py** (데이터 관리용)

#### **목적**: 벡터 스토어 및 데이터 관리
- ✅ **데이터 업로드**: 폴더/파일 단위 업로드
- ✅ **상태 모니터링**: 벡터 스토어 통계
- ✅ **데이터 삭제**: 전체/조건부 삭제
- ✅ **빠른 테스트**: 시스템 동작 확인

#### **사용 시나리오**:
```bash
# 데이터 업로드
python evaluation/manage_data.py --action upload-folder --path 내규

# 시스템 상태 확인
python evaluation/manage_data.py --action status

# 벡터 스토어 통계
python evaluation/manage_data.py --action stats
```

## 📊 확장된 테스트 데이터셋

### **120개 테스트 케이스 구성:**

| 카테고리 | 테스트 케이스 수 | 세부 분류 | 특징 |
|----------|-----------------|-----------|------|
| **🏢 상품** | **50개** | 신용대출(20), 담보대출(15), 기업대출(15) | 실제 PDF 기반 |
| **📋 내규** | **30개** | 윤리강령(15), 인사규정(15) | 회사 규정 전문 |
| **⚖️ 법률** | **20개** | 금융소비자보호법(10), 은행법(10) | 금융 법규 전문 |
| **❓ 일반FAQ** | **20개** | 인터넷뱅킹(10), 계좌관리(10) | RAG 없이 LLM만 |

### **난이도별 분포:**
- **Easy (40개)**: 기본적인 정보 조회
- **Medium (50개)**: 조건이나 절차 관련
- **Hard (30개)**: 복잡한 규정이나 예외사항

## 🎯 권장 테스팅 전략

### **개발 단계별 사용법**

#### **1. 일일 개발 중 (Daily)**
```bash
# 빠른 기능 검증 (대화형 메뉴)
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 기본 테스트 (3개) 선택

# 특정 카테고리만 테스트
python evaluation/pipeline_tester.py
# → 엔드포인트: Intent 라우팅 선택
# → 테스트 유형: 카테고리별 테스트 → 상품 선택
```

#### **2. 기능 완성 후 (Weekly)**
```bash
# 카테고리별 상세 평가 (20-50개)
python evaluation/performance_evaluator.py
# 메뉴에서 4번 선택 → 카테고리 선택

# 난이도별 평가 (30-50개)
python evaluation/performance_evaluator.py
# 메뉴에서 5번 선택 → 난이도 선택

# 파이프라인 비교 테스트
python evaluation/pipeline_tester.py
# → 대량 테스트 (10개 이상) 선택
```

#### **3. 릴리즈 전 (Monthly)**
```bash
# 전체 종합 평가 (120개) - 시간 소요 주의
python evaluation/performance_evaluator.py
# 메뉴에서 3번 선택

# 모든 파이프라인 비교
python evaluation/pipeline_tester.py
# → 각 엔드포인트별로 대량 테스트 실행
```

## 📊 스마트 테스팅 방법

### **1. 카테고리별 집중 테스트**

#### **상품 카테고리 (50개)**
```bash
# 상품 관련만 집중 테스트
python evaluation/performance_evaluator.py
# 메뉴에서 4번 → 1번 (company_products) 선택

# 파이프라인별 비교
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 카테고리별 테스트 → 상품 선택
```

#### **내규 카테고리 (30개)**
```bash
# 내규 관련만 테스트
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 내규 선택
```

#### **법률 카테고리 (20개)**
```bash
# 법률 관련만 테스트
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 법률 선택
```

#### **일반 FAQ (20개)**
```bash
# 일반 FAQ만 테스트
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 일반 FAQ 선택
```

### **2. 난이도별 단계 테스트**

#### **Easy 테스트 (40개) - 기본 검증**
```bash
python evaluation/pipeline_tester.py
# → 테스트 유형: 난이도별 테스트 → easy 선택
```

#### **Medium 테스트 (50개) - 중급 검증**
```bash
python evaluation/performance_evaluator.py
# 메뉴에서 5번 → 2번 (medium) 선택
```

#### **Hard 테스트 (30개) - 고급 검증**
```bash
python evaluation/pipeline_tester.py
# → 테스트 유형: 난이도별 테스트 → hard 선택
```

### **3. 조합 필터링**

#### **상품 + 쉬운 난이도**
```bash
# 1단계: 상품 카테고리 선택
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 상품 선택

# 2단계: 쉬운 난이도만 필터링 (수동으로 질문 선택)
```

#### **내규 + 어려운 난이도**
```bash
# 1단계: 내규 카테고리 선택
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 내규 선택

# 2단계: 어려운 난이도만 필터링 (수동으로 질문 선택)
```

## 📈 성능 모니터링 전략

### **주간 성능 체크 루틴**

#### **1단계: 빠른 검증 (5분)**
```bash
python evaluation/performance_evaluator.py
# 메뉴에서 1번 (빠른 테스트) 선택
```

#### **2단계: 카테고리별 검증 (15분)**
```bash
# 가장 중요한 상품 카테고리 먼저
python evaluation/performance_evaluator.py
# 메뉴에서 4번 → 1번 (company_products) 선택
```

#### **3단계: 실험 검증 (10분)**
```bash
# LangGraph vs 기존 RAG 비교
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 카테고리별 테스트 → 상품 선택
```

### **월간 종합 평가 루틴**

#### **1주차: 카테고리별 완전 평가**
```bash
# 상품 (50개)
python evaluation/performance_evaluator.py → 4번 → 1번

# 내규 (30개)  
python evaluation/performance_evaluator.py → 4번 → 2번

# 법률 (20개)
python evaluation/performance_evaluator.py → 4번 → 3번

# 일반FAQ (20개)
python evaluation/performance_evaluator.py → 4번 → 4번
```

#### **2주차: 난이도별 평가**
```bash
# Easy (40개)
python evaluation/performance_evaluator.py → 5번 → 1번

# Medium (50개)
python evaluation/performance_evaluator.py → 5번 → 2번

# Hard (30개)
python evaluation/performance_evaluator.py → 5번 → 3번
```

#### **3주차: 전체 종합 평가**
```bash
# 전체 120개 (시간 소요 주의)
python evaluation/performance_evaluator.py → 3번
```

## 💡 효율적인 테스팅 팁

### **1. 시간 관리**
| 테스트 규모 | 예상 시간 | 권장 사용 시점 |
|-------------|-----------|----------------|
| 빠른 테스트 (4개) | ~2분 | 매일 |
| 카테고리별 (20-50개) | ~10-25분 | 주간 |
| 난이도별 (30-50개) | ~15-25분 | 주간 |
| 전체 평가 (120개) | ~60분 | 월간 |

### **2. 우선순위 테스팅**
```bash
# 1순위: 상품 카테고리 (비즈니스 핵심)
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 상품 선택

# 2순위: 쉬운 난이도 (기본 기능 검증)
python evaluation/pipeline_tester.py
# → 테스트 유형: 난이도별 테스트 → easy 선택

# 3순위: 내규 카테고리 (컴플라이언스)
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 내규 선택
```

### **3. 문제 진단 및 해결**

#### **성능 저하 발견 시:**
```bash
# 1단계: 특정 카테고리 문제인지 확인
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → [문제_카테고리] 선택

# 2단계: 난이도별 문제인지 확인
python evaluation/pipeline_tester.py
# → 테스트 유형: 난이도별 테스트 → hard 선택

# 3단계: 특정 질문으로 상세 디버깅
python evaluation/pipeline_tester.py
# → 테스트 유형: 직접 질문 입력 → "문제 질문" 입력
```

#### **새 기능 검증 시:**
```bash
# 1단계: 빠른 검증
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 난이도별 테스트 → easy 선택

# 2단계: 관련 카테고리 집중 테스트
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 카테고리별 테스트 → [관련_카테고리] 선택

# 3단계: 어려운 케이스 도전
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 난이도별 테스트 → hard 선택
```

## 🎯 권장 사용 전략

### **통합 vs 분리 비교**

| 측면 | 통합 evaluation 폴더 | 기존 분리 구조 |
|------|---------------------|----------------|
| **사용 편의성** | ✅ 한 곳에서 모든 평가 | ❌ 여러 폴더 이동 |
| **유지보수** | ✅ 통합 관리 | ❌ 중복 코드 |
| **성능** | ✅ 스마트 필터링 | ❌ 전체 실행만 |
| **확장성** | ✅ 통합 데이터셋 | ❌ 개별 관리 |
| **학습 곡선** | ✅ 일관된 인터페이스 | ❌ 도구별 학습 |

### **단계별 테스팅 가이드라인**

#### **개발 초기 (Daily)**
- **빠른 검증**: 3-5개 테스트 케이스
- **도구**: `pipeline_tester.py` (대화형 메뉴)
- **시간**: 2-5분

#### **기능 개발 중 (Weekly)**  
- **카테고리별 테스트**: 20-50개 케이스
- **도구**: `performance_evaluator.py` (메뉴 4번)
- **시간**: 10-25분

#### **릴리즈 준비 (Monthly)**
- **전체 종합 평가**: 120개 케이스
- **도구**: `performance_evaluator.py` (메뉴 3번)
- **시간**: 60분

## 🔍 문제 해결 가이드

### **1. 성능 저하 발견**
```bash
# Step 1: 카테고리별 문제 격리
python evaluation/pipeline_tester.py
# → 테스트 유형: 카테고리별 테스트 → 상품 선택

# Step 2: 난이도별 분석
python evaluation/pipeline_tester.py
# → 테스트 유형: 난이도별 테스트 → hard 선택

# Step 3: 특정 질문 상세 분석
python evaluation/pipeline_tester.py
# → 테스트 유형: 직접 질문 입력 → "문제 질문" 입력
```

### **2. 새 기능 검증**
```bash
# Step 1: LangGraph 기능 검증
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 난이도별 테스트 → easy 선택

# Step 2: 기존 방식과 비교
python evaluation/pipeline_tester.py
# → 엔드포인트: Intent 라우팅 선택
# → 테스트 유형: 카테고리별 테스트 → 상품 선택

# Step 3: 어려운 케이스 도전
python evaluation/performance_evaluator.py → 5번 → 3번 (hard)
```

### **3. 데이터 품질 검증**
```bash
# Step 1: 데이터 업로드 상태 확인
python evaluation/manage_data.py --action stats

# Step 2: 카테고리별 검색 성능 확인
python evaluation/performance_evaluator.py → 4번

# Step 3: 문제 데이터 제거
python evaluation/manage_data.py --action delete-condition --field [필드] --value [값]
```

## 🚀 고급 활용법

### **1. 배치 스크립트 작성**
```bash
#!/bin/bash
# weekly_test.sh
echo "주간 RAG 성능 체크 시작..."

# 상품 카테고리 테스트 (performance_evaluator 사용)
python evaluation/performance_evaluator.py
# 메뉴에서 4번 → 1번 (company_products) 선택

# LangGraph 실험 (pipeline_tester 사용)
python evaluation/pipeline_tester.py
# → 엔드포인트: LangGraph 선택
# → 테스트 유형: 난이도별 테스트 → easy 선택

echo "주간 테스트 완료!"
```

### **2. 성능 모니터링 자동화**
```python
# performance_monitor.py
import subprocess
import datetime

def daily_check():
    """일일 성능 체크"""
    result = subprocess.run([
        "python", "evaluation/rag_flow_checker.py", 
        "--type", "langgraph", "--difficulty", "easy"
    ], capture_output=True, text=True)
    
    with open(f"daily_check_{datetime.date.today()}.log", "w") as f:
        f.write(result.stdout)

if __name__ == "__main__":
    daily_check()
```

### **3. 결과 비교 분석**
```bash
# 결과 저장 후 비교
python evaluation/rag_flow_checker.py --type rag --save baseline_results.json
python evaluation/rag_flow_checker.py --type langgraph --save langgraph_results.json

# JSON 결과 비교
jq '.[] | {question: .question, rag_time: .result.response_time}' baseline_results.json
jq '.[] | {question: .question, langgraph_time: .result.response_time}' langgraph_results.json
```

## 🔮 결론 및 권장사항

### **✅ 통합 evaluation 폴더 장점**
1. **효율적 관리** - 모든 평가 도구가 한 곳에
2. **스마트 필터링** - 카테고리/난이도별 선택 테스트
3. **확장된 데이터셋** - 120개 다양한 테스트 케이스
4. **일관된 인터페이스** - 통일된 사용법

### **🎯 권장 사용 패턴**
1. **일일**: 빠른 테스트 (3-5개)
2. **주간**: 카테고리별 테스트 (20-50개)
3. **월간**: 전체 종합 평가 (120개)

### **💡 핵심 포인트**
- **시간 관리**: 필요에 따라 적절한 규모 선택
- **우선순위**: 비즈니스 중요도에 따른 카테고리 우선 테스트
- **점진적 확장**: 쉬운 → 어려운 순서로 단계적 검증

**통합된 evaluation 시스템으로 더 체계적이고 효율적인 RAG 성능 관리가 가능해졌습니다!**