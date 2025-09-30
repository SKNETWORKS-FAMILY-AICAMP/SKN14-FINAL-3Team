"""
KB금융그룹 RAG Agent - Data Models
==================================
Pydantic 모델과 TypedDict를 사용한 타입 안전한 데이터 구조 정의
"""

import operator
from collections.abc import Sequence
from enum import Enum
from typing import Annotated, Any, Optional, Union, Dict, List
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


# ========== Enum Definitions ==========



class ConversationMode(str, Enum):
    """대화 모드"""
    TOOL_CALLING = "tool_calling"
    DIRECT = "direct"


class ProductType(str, Enum):
    """상품 유형 (메인 카테고리)"""
    LOAN = "loan"
    DEPOSIT = "deposit"
    SAVINGS = "savings"
    CARD = "card"
    INSURANCE = "insurance"
    FUND = "fund"


class LoanSubType(str, Enum):
    """대출 상품 세부 유형"""
    PERSONAL_SECURED_JEONSE = "개인_담보_전세대출"
    PERSONAL_CREDIT = "개인_신용대출"
    PERSONAL_AUTO = "개인_자동차_대출"
    PERSONAL_HOUSING_FUND = "개인_주택도시기금대출"
    BUSINESS_LOAN = "기업_대출"


class DepositSubType(str, Enum):
    """예금 상품 세부 유형"""
    DEMAND_DEPOSIT = "요구불예금"
    TIME_DEPOSIT = "정기예금"
    INSTALLMENT_DEPOSIT = "정기적금"
    FREE_DEPOSIT = "자유적금"


class CardSubType(str, Enum):
    """카드 상품 세부 유형"""
    CREDIT_CARD = "신용카드"
    DEBIT_CARD = "체크카드"
    PREPAID_CARD = "선불카드"
    CORPORATE_CARD = "법인카드"


class SavingsSubType(str, Enum):
    """적금 상품 세부 유형"""
    REGULAR_SAVINGS = "정기적금"
    FREE_SAVINGS = "자유적금"
    HOUSING_SAVINGS = "주택청약적금"
    PENSION_SAVINGS = "연금저축"


# ========== Pydantic Models ==========

class SessionContext(BaseModel):
    """세션 컨텍스트"""
    session_id: str = Field(description="세션 고유 식별자")
    created_at: str = Field(description="세션 생성 시간")
    last_accessed: str = Field(description="마지막 접근 시간")
    conversation_turns: int = Field(default=0, description="대화 턴 수")
    session_title: str = Field(default="", description="세션 제목")
    is_first_turn: bool = Field(default=True, description="첫 대화 여부")
    
    # session_manager.py와의 호환성을 위한 추가 필드들
    last_activity: str = Field(default="", description="마지막 활동 시간")
    initial_intent: str = Field(default="", description="초기 의도")
    current_topic: str = Field(default="", description="현재 주제")
    conversation_summary: str = Field(default="", description="대화 요약")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="사용자 선호도")
    active_product: Optional[str] = Field(default=None, description="활성 상품")
    conversation_mode: str = Field(default="normal", description="대화 모드")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """딕셔너리에서 객체 생성"""
        return cls(**data)


class ConversationTurn(BaseModel):
    """대화 턴"""
    turn_id: str = Field(description="턴 고유 식별자")
    query: str = Field(description="사용자 질문")
    response: str = Field(description="AI 응답")
    product_name: str = Field(default="", description="추출된 상품명")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="참조 문서")
    timestamp: str = Field(description="생성 시간")


class DocumentSource(BaseModel):
    """문서 소스 정보"""
    file_name: str = Field(description="파일명")
    page_number: int = Field(description="페이지 번호")
    content: str = Field(description="문서 내용")
    main_category: str = Field(description="메인 카테고리 (상품, 내규, 규제 등)")
    sub_category: str = Field(description="서브 카테고리 (개인_신용대출, 기업_대출 등)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")




class ProductExtractionResult(BaseModel):
    """상품명 추출 결과"""
    product_name: str = Field(description="추출된 상품명")
    product_type: Optional[ProductType] = Field(default=None, description="상품 유형 (메인 카테고리)")
    sub_category: Optional[str] = Field(default=None, description="서브 카테고리 (metadata용)")
    confidence: float = Field(ge=0.0, le=1.0, description="추출 신뢰도")
    reasoning: str = Field(description="추출 근거")


class GuardrailResult(BaseModel):
    """가드레일 검사 결과"""
    is_compliant: bool = Field(description="규정 준수 여부")
    violations: List[str] = Field(default_factory=list, description="위반 사항")
    compliant_response: str = Field(description="규정 준수 응답")
    original_response: str = Field(description="원본 응답")


class RAGSearchResult(BaseModel):
    """RAG 검색 결과"""
    query: str = Field(description="검색 쿼리")
    retrieved_docs: List[DocumentSource] = Field(description="검색된 문서들")
    context_text: str = Field(description="컨텍스트 텍스트")
    search_time: float = Field(description="검색 시간")
    total_docs: int = Field(description="총 문서 수")


class WorkflowExecutionResult(BaseModel):
    """워크플로우 실행 결과"""
    success: bool = Field(description="실행 성공 여부")
    response: str = Field(description="최종 응답")
    product_name: str = Field(default="", description="상품명")
    sources: List[DocumentSource] = Field(default_factory=list, description="참조 문서")
    session_info: SessionContext = Field(description="세션 정보")
    execution_time: float = Field(description="실행 시간")
    error_message: Optional[str] = Field(default=None, description="에러 메시지")


# ========== TypedDict for LangGraph State ==========

class RAGState(TypedDict):
    """LangGraph RAG 워크플로우 상태"""
    # Core conversation data
    messages: Annotated[Sequence[Union[BaseMessage, dict]], operator.add]
    query: str
    response: str
    
    # Session management
    session_context: Optional[SessionContext]
    conversation_history: List[ConversationTurn]
    turn_id: str
    
    
    # Product extraction
    product_name: str
    product_extraction_result: Optional[ProductExtractionResult]
    
    # Document retrieval
    retrieved_docs: List[DocumentSource]
    context_text: str
    sources: List[Dict[str, Any]]
    
    # Guardrail
    guardrail_decision: str
    violations: List[str]
    compliant_response: str
    
    # Control flags
    ready_to_answer: bool
    needs_clarification: bool
    query_complete: bool
    
    # Workflow execution tracking
    execution_path: List[str]
    
    # Metadata
    category: str
    conversation_mode: str
    initial_intent: str
    initial_topic_summary: str
    current_topic: str
    active_product: str


# ========== Response Models ==========

class APIResponse(BaseModel):
    """API 응답 모델"""
    status: str = Field(description="응답 상태")
    response: str = Field(description="응답 내용")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="참조 문서")
    category: str = Field(description="카테고리")
    product_name: str = Field(default="", description="상품명")
    session_info: SessionContext = Field(description="세션 정보")
    initial_intent: str = Field(default="", description="초기 의도")
    initial_topic_summary: str = Field(default="", description="초기 주제 요약")
    conversation_mode: str = Field(description="대화 모드")
    current_topic: str = Field(default="", description="현재 주제")
    active_product: str = Field(default="", description="활성 상품")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    success: bool = Field(default=False, description="성공 여부")
    status: str = Field(description="에러 상태")
    error: str = Field(description="에러 메시지")
    session_id: Optional[str] = Field(default=None, description="세션 ID")
    error_code: Optional[str] = Field(default=None, description="에러 코드")
    timestamp: str = Field(description="에러 발생 시간")


# ========== Configuration Models ==========

class WorkflowConfig(BaseModel):
    """워크플로우 설정"""
    max_turns: int = Field(default=50, description="최대 대화 턴 수")
    max_messages: int = Field(default=100, description="최대 메시지 수")
    search_k: int = Field(default=5, description="검색 문서 수")
    enable_guardrail: bool = Field(default=True, description="가드레일 활성화")
    enable_intent_classification: bool = Field(default=True, description="의도 분류 활성화")
    enable_product_extraction: bool = Field(default=True, description="상품명 추출 활성화")


class SessionConfig(BaseModel):
    """세션 설정"""
    session_timeout: int = Field(default=3600, description="세션 타임아웃 (초)")
    max_conversation_turns: int = Field(default=50, description="최대 대화 턴 수")
    enable_title_generation: bool = Field(default=True, description="제목 생성 활성화")
    title_max_length: int = Field(default=15, description="제목 최대 길이")
