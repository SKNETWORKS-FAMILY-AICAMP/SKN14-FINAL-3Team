# LangGraph RAG Workflow Documentation

## 📁 폴더 구조 개요

```
src/langgraph/
├── graph.py                    # 워크플로우 그래프 정의 및 노드 연결
├── nodes.py                    # 모든 노드 함수들 (939줄)
├── agent.py                    # RAGAgent 클래스 (메인 에이전트)
├── models.py                   # Pydantic 모델 및 TypedDict 정의
├── utils.py                    # 공통 유틸리티 함수들 (싱글톤, 캐싱)
├── tools.py                    # LangChain 도구 정의
├── session_manager.py          # 세션 관리 클래스
├── langgraph_v2.py            # 호환성 유지를 위한 진입점
├── prompts.yaml               # 프롬프트 템플릿 (215줄)
├── guardrails/                # 가드레일 설정
│   ├── glossary_terms.yaml    # 금융 용어 정의
│   └── policy_rules.yaml      # 정책 규칙 정의
└── README.md                  # 이 문서
```

## 🎯 전체 아키텍처

### **LangGraph V2 워크플로우 구조**
- **지능형 라우팅**: LLM 기반 노드 선택으로 정확한 경로 결정
- **멀티턴 대화**: 세션 관리와 맥락 유지를 통한 연속 대화 지원
- **성능 최적화**: 싱글톤 패턴과 캐싱을 통한 메모리 효율성
- **가드레일 시스템**: 응답 품질 보장 및 금융 규제 준수

## 📋 각 파일 상세 설명

### 1. `graph.py` - 워크플로우 그래프 정의
**역할**: LangGraph 워크플로우의 핵심 구조 정의
**주요 기능**:
- `create_rag_workflow()` 함수로 워크플로우 생성
- 노드 간 연결 및 조건부 라우팅 설정
- 싱글톤 SLM/VectorStore 인스턴스 사용
- 워크플로우 컴파일 및 반환

```python
def create_rag_workflow(checkpointer=None, llm=None) -> Runnable:
    """RAG 워크플로우 생성"""
    slm = get_shared_slm()  # 싱글톤 인스턴스
    workflow = StateGraph(RAGState)
    
    # 노드 추가 및 연결
    workflow.add_node(SESSION_INIT, session_init_node)
    workflow.add_node(SUPERVISOR, supervisor_with_llm)
    # ... 기타 노드들
    
    return workflow.compile(checkpointer=checkpointer)
```

### 2. `nodes.py` - 노드 함수들 (939줄)
**역할**: 워크플로우의 각 단계별 실행 함수들
**주요 기능**:
- 8개의 핵심 노드 함수 정의
- 실행 경로 추적 및 상태 변경 로깅
- 성능 최적화된 구현
- 에러 처리 및 폴백 로직

#### **노드 함수 목록**:
1. `session_init_node()` - 세션 초기화 및 대화 히스토리 로드
2. `supervisor_node()` - LLM 기반 지능형 라우팅
3. `supervisor_router()` - 라우팅 결정 로직
4. `product_extraction_node()` - 상품명 추출
5. `product_search_node()` - 상품별 검색
6. `session_summary_node()` - 세션 제목 생성 (첫 대화)
7. `rag_search_node()` - RAG 문서 검색
8. `context_answer_node()` - 맥락 기반 답변
9. `guardrail_check_node()` - 응답 검증
10. `answer_node()` - 최종 답변 생성

```python
def supervisor_node(state: RAGState, llm=None, slm: SLM = None) -> RAGState:
    """중앙 관리자 - 툴 선택"""
    # 첫 대화인지 확인
    is_first_turn = not conversation_history or len(conversation_history) == 0
    
    if is_first_turn:
        # 도구를 사용하여 라우팅
        from .tools import answer, rag_search, product_extraction, context_answer
        tool_functions = [answer, rag_search, product_extraction, context_answer]
        result = slm.llm.bind_tools(tool_functions, tool_choice="required").invoke(supervisor_prompt)
    else:
        # 멀티턴 대화 처리
        # 맥락 기반 답변 우선 고려
```

### 3. `agent.py` - RAGAgent 클래스
**역할**: 통합된 에이전트 인터페이스 제공
**주요 기능**:
- `RAGAgent` 클래스로 통합 인터페이스
- Django와의 통합 지원
- 스트리밍 및 일반 실행 모드
- 에러 처리 및 상태 관리

```python
class RAGAgent:
    def __init__(self, checkpointer=None, config=None):
        self.slm = get_shared_slm()
        self.vector_store = get_shared_vector_store()
        self.workflow = create_rag_workflow(checkpointer=self.checkpointer, llm=self.slm.llm)
    
    def chat(self, message: str, session_id: str = None, stream: bool = False, **kwargs):
        """통합 채팅 인터페이스"""
        # Django 대화 히스토리 처리
        # 워크플로우 실행
        # 결과 반환
```

### 4. `models.py` - 데이터 모델 정의
**역할**: 타입 안전성을 위한 데이터 구조 정의
**주요 기능**:
- Pydantic 모델과 TypedDict 정의
- 세션 컨텍스트 및 대화 턴 모델
- API 응답 및 에러 모델
- 설정 모델

```python
class RAGState(TypedDict):
    """LangGraph RAG 워크플로우 상태"""
    messages: Annotated[Sequence[Union[BaseMessage, dict]], operator.add]
    query: str
    response: str
    session_context: Optional[SessionContext]
    conversation_history: List[ConversationTurn]
    # ... 기타 상태 필드들
```

### 5. `utils.py` - 공통 유틸리티 (772줄)
**역할**: 공통 기능 및 성능 최적화
**주요 기능**:
- 싱글톤 패턴으로 SLM/VectorStore 관리
- 프롬프트 캐싱 및 로드
- 검색 결과 캐싱
- 가드레일 검사 로직
- 상품명 추출 및 분류

```python
class SLMManager:
    """SLM 인스턴스를 싱글톤으로 관리"""
    _instance = None
    _slm_instance = None
    
    def get_slm(self):
        if self._slm_instance is None:
            from ..slm.slm import SLM
            self._slm_instance = SLM()
        return self._slm_instance
```

### 6. `tools.py` - LangChain 도구 정의
**역할**: LangChain @tool 데코레이터로 정의된 도구들
**주요 기능**:
- 9개의 도구 함수 정의
- supervisor_node에서 사용 가능한 도구 목록
- 각 도구의 스키마와 설명 제공

```python
@tool(parse_docstring=True)
def rag_search(thought: str, query: str):
    """Search documents using RAG for specific information."""
    
@tool(parse_docstring=True)
def product_extraction(thought: str, query: str):
    """Extract product name from user query."""
```

### 7. `session_manager.py` - 세션 관리
**역할**: 대화 세션 및 히스토리 관리
**주요 기능**:
- `SessionManager` 클래스로 세션 생성/관리
- Django와의 통합을 통한 대화 히스토리 로드
- 세션 만료 처리 및 자동 정리
- 컨텍스트 추적 및 메시지 히스토리 관리

```python
class SessionManager:
    def create_session(self, session_id: str = None) -> SessionContext:
        """새 세션 생성"""
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationTurn]:
        """Django에서 대화 히스토리 로드"""
```

### 8. `prompts.yaml` - 프롬프트 템플릿 (215줄)
**역할**: 모든 프롬프트 템플릿 중앙 관리
**주요 기능**:
- 시스템 프롬프트 정의
- 라우팅 프롬프트 정의
- 에러 메시지 정의
- 가드레일 설정

```yaml
system_prompts:
  supervisor:
    system: |
      당신은 KB금융그룹의 중앙 관리자입니다...
  rag_system:
    system: |
      당신은 KB금융그룹의 내부 시스템입니다...
```

## 🔄 워크플로우 실행 흐름

### **1단계: 세션 초기화**
```
SESSION_INIT → 세션 생성/조회 → 대화 히스토리 로드
```

### **2단계: 첫 대화 vs 멀티턴 판단**
```
first_turn_router → 첫 대화면 SESSION_SUMMARY, 아니면 SUPERVISOR
```

### **3단계: 지능형 라우팅**
```
SUPERVISOR → LLM 기반 도구 선택 → 다음 노드로 라우팅:
├── rag_search (문서 검색)
├── product_extraction (상품명 추출)
├── answer (일반 FAQ)
└── context_answer (맥락 기반 답변)
```

### **4단계: 특화 노드 실행**
```
├── PRODUCT_EXTRACTION → PRODUCT_SEARCH → ANSWER
├── RAG_SEARCH → ANSWER
├── CONTEXT_ANSWER → 조건부 라우팅
└── ANSWER (직접)
```

### **5단계: 가드레일 검사**
```
ANSWER → GUARDRAIL_CHECK → 최종 응답
```

## 🚀 성능 최적화

### **싱글톤 패턴**
- **SLM 인스턴스**: `get_shared_slm()`으로 중복 생성 방지
- **VectorStore 인스턴스**: `get_shared_vector_store()`로 메모리 효율성
- **프롬프트 캐싱**: YAML 파일을 한 번만 로드하여 재사용

### **고급 캐싱 시스템**
- **TTL 기반 캐시**: 5분 TTL로 자동 만료 처리
- **LRU 캐시 관리**: 가장 오래된 항목부터 제거
- **캐시 크기 제한**: 메모리 누수 방지 (최대 100개 항목)
- **자동 캐시 정리**: `cleanup_expired_cache()` 함수로 주기적 정리

### **검색 최적화**
- **검색 결과 캐싱**: 동일한 쿼리에 대한 결과 재사용
- **문서 수 제한**: k=3으로 검색 결과 수 최적화
- **메타데이터 필터링**: 상품별 정확한 검색
- **쿼리 길이 최적화**: `optimize_query_length()`로 긴 쿼리 처리

### **메모리 관리**
- **대화 히스토리 제한**: 최대 10개 턴으로 제한
- **메시지 히스토리 제한**: 최대 50개 메시지로 제한
- **컨텍스트 길이 제한**: 최대 2000자로 제한
- **배치 처리**: `batch_process_items()`로 대량 데이터 처리

### **성능 모니터링**
- **실행 시간 추적**: `log_performance()` 함수로 1초 이상 작업만 로깅
- **메모리 사용량 모니터링**: `get_memory_usage()`로 실시간 모니터링
- **조건부 로깅**: DEBUG 모드에서만 상세 로깅
- **캐시 히트율 추적**: 캐시 효율성 모니터링

## 📊 지능형 라우팅 시스템

### **라우팅 우선순위**
1. **최우선**: 상품명이 명확히 언급 → `product_extraction`
2. **두 번째**: 이전 대화 맥락만으로 답변 가능 → `context_answer`
3. **세 번째**: 일반적인 지식으로 답변 가능 → `answer`
4. **기본**: 그 외의 경우 → `rag_search`

### **맥락 기반 답변**
- 이전 대화에서 상품을 설명했다면, 그 상품에 대한 모든 후속 질문은 `context_answer` 선택
- "나이 제한이 있나요?", "조건은 어떻게 되나요?" 등 구체적인 조건 질문 처리

## 🔧 사용법

### **기본 사용법**
```python
from src.langgraph.agent import RAGAgent

# 에이전트 생성
agent = RAGAgent()

# 채팅 실행
result = agent.chat(
    message="햇살론 대출에 대해 알려주세요",
    session_id="user_123"
)

print(result["response"])
```

### **Django 통합**
```python
def send_message_with_langgraph_rag(message: str, session_id: str, chat_history: List[Dict[str, Any]] = None):
    """Django에서 호출하는 함수"""
    agent = RAGAgent()
    result = agent.chat(message, session_id, chat_history=chat_history)
    return result
```

### **스트리밍 모드**
```python
# 스트리밍 실행
for chunk in agent.chat(message, session_id, stream=True):
    print(chunk)
```

## 🛡️ 가드레일 시스템

### **응답 검증**
- **완전성 검사**: 응답 길이 및 완성도 확인
- **정확성 검사**: 금융 정보의 정확성 검증
- **용어 정규화**: 금융 용어 표준화
- **구조 검사**: 응답 형식 및 강조 적용

### **가드레일 설정 파일**
- `guardrails/glossary_terms.yaml`: 금융 용어 정의
- `guardrails/policy_rules.yaml`: 정책 규칙 및 검증 로직

## 📝 로깅 시스템

### **노드별 로깅**
```python
logger.info("🏷️ [NODE] product_extraction_node 실행 시작")
logger.info("🔍 [NODE] product_search_node 실행 시작")
logger.info("📚 [NODE] rag_search_node 실행 시작")
```

### **성능 모니터링**
```python
start_time = time.time()
# ... 노드 실행 ...
end_time = time.time()
logger.info(f"📝 [NODE] node_name 완료 - 실행시간: {execution_time:.2f}초")
```

## 🔄 멀티턴 대화

### **세션 관리**
- Django와의 통합을 통한 대화 히스토리 로드
- 세션별 컨텍스트 유지
- 자동 세션 만료 및 정리

### **맥락 유지**
- 이전 대화 내용을 고려한 답변 생성
- 상품별 연속 질문 처리
- 대화 흐름의 자연스러운 연결

## 📈 성능 모니터링

### **실행 경로 추적**
```python
def track_execution_path(state: RAGState, node_name: str) -> RAGState:
    """실행 경로를 추적하는 헬퍼 함수"""
    execution_path = state.get("execution_path", [])
    execution_path.append(node_name)
    return {**state, "execution_path": execution_path}
```

### **상태 변경 추적**
```python
def track_state_changes(state: RAGState, change_type: str, details: str = "") -> RAGState:
    """상태 변경 추적"""
    state_changes = state.get("state_changes", [])
    state_changes.append({
        "type": change_type,
        "details": details,
        "timestamp": time.time()
    })
    return {**state, "state_changes": state_changes}
```

## 🐛 에러 처리

### **포괄적 에러 처리**
- 모든 노드에서 `try-except` 블록으로 에러 처리
- `create_error_response()` 함수로 일관된 에러 응답
- 로깅을 통한 디버깅 지원

### **에러 메시지 (prompts.yaml)**
```yaml
error_messages:
  general_error: "시스템 오류가 발생했습니다."
  search_error: "검색 중 오류가 발생했습니다. 다시 시도해주세요."
  timeout_error: "요청 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
  no_documents: "관련 문서를 찾을 수 없습니다. 다른 키워드로 검색해보세요."
```

## 🎯 핵심 특징

### **✅ 지능형 라우팅**
- LLM 기반 도구 선택으로 정확한 경로 결정
- 맥락을 고려한 멀티턴 대화 처리
- 상품별 특화된 검색 및 답변

### **✅ 성능 최적화**
- 싱글톤 패턴으로 메모리 효율성
- 검색 결과 캐싱으로 속도 향상
- 적절한 제한으로 메모리 누수 방지

### **✅ 확장성**
- 모듈화된 구조로 새로운 노드 추가 용이
- YAML 기반 설정으로 프롬프트 관리
- Django와의 원활한 통합

### **✅ 안정성**
- 포괄적인 에러 처리
- 가드레일 시스템으로 응답 품질 보장
- 상세한 로깅으로 디버깅 지원

---

## 🎯 요약

이 `langgraph` 폴더는 **프로덕션 레벨의 완성도**를 가진 RAG 워크플로우를 제공하며, 다음과 같은 특징을 가집니다:

- ✅ **지능형 라우팅**: LLM 기반 정확한 노드 선택
- ✅ **멀티턴 대화**: 세션 관리와 맥락 유지
- ✅ **성능 최적화**: 싱글톤 패턴과 캐싱
- ✅ **가드레일 시스템**: 응답 품질 보장
- ✅ **Django 통합**: 원활한 웹 애플리케이션 연동
- ✅ **확장성**: 모듈화된 구조로 유지보수 용이
- ✅ **안정성**: 포괄적인 에러 처리와 로깅

이 구조를 통해 **확장 가능하고 유지보수하기 쉬운** 고품질 RAG 시스템을 구축할 수 있습니다.
이 구조를 통해 **확장 가능하고 유지보수하기 쉬운** RAG 시스템을 구축할 수 있습니다.