"""
KB금융그룹 RAG Agent - Graph Architecture
========================================
Main workflow implementation with proper node organization, 
routing, and subgraph composition.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from functools import partial

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph

from .models import RAGState
from .nodes import (
    session_init_node,
    supervisor_node,
    supervisor_router,
    product_extraction_node,
    product_search_node,
    session_summary_node,
    rag_search_node,
    context_answer_node,
    guardrail_check_node,
    answer_node
)
from .utils import get_shared_slm, get_shared_vector_store

logger = logging.getLogger(__name__)

# ========== Node Constants ==========

# Main workflow nodes
SESSION_INIT = "session_init"
SUPERVISOR = "supervisor"
PRODUCT_EXTRACTION = "product_extraction"
PRODUCT_SEARCH = "product_search"
SESSION_SUMMARY = "session_summary"
RAG_SEARCH = "rag_search"
CONTEXT_ANSWER = "context_answer"  # 맥락 기반 답변 노드
GUARDRAIL_CHECK = "guardrail_check"
ANSWER = "answer"


# ========== Utility Functions ==========

def join_graph(response: dict) -> dict:
    """Join graph utility for subgraph integration"""
    messages = response.get("messages", [])
    if messages:
        return {"messages": [messages[-1]]}
    return response


# ========== Router Functions ==========

def start_router(state: RAGState) -> list[str]:
    """Initial routing - always go to session_init"""
    return [SESSION_INIT]

def first_turn_router(state: RAGState) -> str:
    """첫 대화인지 확인하여 라우팅"""
    conversation_history = state.get("conversation_history", [])
    is_first_turn = not conversation_history or len(conversation_history) == 0
    
    if is_first_turn:
        return "session_summary"
    else:
        return "supervisor"




# ========== Main Graph Factory Function ==========

def create_rag_workflow(
    checkpointer: BaseCheckpointSaver | None = None,
    llm: Any = None
) -> Runnable:
    """
    Create RAG workflow following the specified scenario:
    SESSION_INIT -> SESSION_SUMMARY -> SUPERVISOR -> SPECIALIZED_NODES -> ANSWER
    
    Args:
        checkpointer: Checkpoint saver for conversation persistence
        llm: Language model for supervisor node operations (required!)
        
    Returns:
        Compiled StateGraph workflow
    """
    # 싱글톤 SLM 인스턴스 사용 (메모리 효율성)
    slm = get_shared_slm()
    if not llm:
        llm = slm.llm
    
    workflow = StateGraph(RAGState)
    
    # ========== Core Workflow Construction ==========
    
    # Initialize state
    workflow.add_node(SESSION_INIT, session_init_node)
    workflow.add_edge(START, SESSION_INIT)
    
    # SESSION_INIT 후 첫 대화인지 확인하여 라우팅
    workflow.add_conditional_edges(
        SESSION_INIT,
        first_turn_router,
        ["session_summary", "supervisor"]
    )
    
    # Supervisor node - LLM-based routing with tool calling
    supervisor_with_llm = partial(supervisor_node, llm=llm, slm=slm)
    workflow.add_node(SUPERVISOR, supervisor_with_llm)
    
    # SUPERVISOR는 도구 선택 후 supervisor_router로 라우팅
    workflow.add_conditional_edges(
        SUPERVISOR,
        supervisor_router,
        ["rag_search", "product_extraction", "answer", "context_answer"]
    )
    
    # Product extraction node
    product_extraction_with_slm = partial(product_extraction_node, slm=slm)
    workflow.add_node(PRODUCT_EXTRACTION, product_extraction_with_slm)
    workflow.add_edge(PRODUCT_EXTRACTION, PRODUCT_SEARCH)
    
    # Product search node
    product_search_with_slm = partial(product_search_node, slm=slm)
    workflow.add_node(PRODUCT_SEARCH, product_search_with_slm)
    workflow.add_edge(PRODUCT_SEARCH, ANSWER)
    
    # Session summary node for first turn only
    session_summary_with_slm = partial(session_summary_node, slm=slm)
    workflow.add_node(SESSION_SUMMARY, session_summary_with_slm)
    
    # SESSION_SUMMARY 후 SUPERVISOR로 라우팅 (첫 대화만)
    workflow.add_edge(SESSION_SUMMARY, SUPERVISOR)
    
    # RAG search node (싱글톤 VectorStore 인스턴스 사용)
    vector_store = get_shared_vector_store()
    rag_search_with_slm = partial(rag_search_node, slm=slm, vector_store=vector_store)
    
    workflow.add_node(RAG_SEARCH, rag_search_with_slm)
    workflow.add_edge(RAG_SEARCH, ANSWER)
    
    # Context answer node - 맥락 기반 답변
    context_answer_with_slm = partial(context_answer_node, slm=slm)
    workflow.add_node(CONTEXT_ANSWER, context_answer_with_slm)
    
    # Context answer에서 조건부 라우팅 (검색 필요시 RAG/Product, 아니면 ANSWER)
    def context_answer_router(state: RAGState) -> str:
        """Context answer에서 조건부 라우팅"""
        if state.get("redirect_to_rag"):
            # RAG 검색이 필요한 경우
            if state.get("product_name"):
                return "product_extraction"  # 상품 검색
            else:
                return "rag_search"  # 일반 RAG 검색
        else:
            return "answer"  # 맥락 기반 답변 완료
    
    workflow.add_conditional_edges(
        CONTEXT_ANSWER,
        context_answer_router,
        ["answer", "rag_search", "product_extraction"]
    )
    
    # Answer node - final response generation
    workflow.add_node(ANSWER, answer_node)
    workflow.add_edge(ANSWER, GUARDRAIL_CHECK)
    
    # Guardrail check node - 모든 답변 후 자동 실행
    guardrail_check_with_slm = partial(guardrail_check_node, slm=slm)
    workflow.add_node(GUARDRAIL_CHECK, guardrail_check_with_slm)
    workflow.add_edge(GUARDRAIL_CHECK, END)
    
    return workflow.compile(
        checkpointer=checkpointer or MemorySaver(),
        debug=False,
        # 성능 최적화 옵션
        interrupt_before=[],  # 인터럽트 없음
        interrupt_after=[],   # 인터럽트 없음
    )


# ========== Factory Functions ==========

def create_agent():
    """Create agent instance with automatic LLM configuration"""
    from .agent import RAGAgent
    return RAGAgent()


# ========== Simple Chat Interface Functions ==========
# Simplified interface without heavy dependencies

def chat_send_message(message: str, session_id: str = "default") -> Dict[str, Any]:
    """Send message in chat - simplified interface"""
    try:
        # Create workflow with default settings
        workflow = create_rag_workflow()
        
        # Basic state for testing
        initial_state = {
            "messages": [],
            "query": message,
            "category": "",
            "product_name": "",
            "retrieved_docs": [],
            "context_text": "",
            "response": "",
            "sources": [],
            "session_context": None,
            "conversation_history": [],
            "turn_id": "",
            "guardrail_decision": "",
            "violations": [],
            "compliant_response": "",
        }
        
        result = workflow.invoke(initial_state)
        return {
            "response": result.get("response", "처리 중 오류가 발생했습니다."),
            "session_id": session_id,
            "success": True
        }
    except Exception as e:
        return {
            "response": f"오류가 발생했습니다: {str(e)}",
            "session_id": session_id,
            "success": False,
            "error": str(e)
        }


def api_chat(message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """API method for web frontends - simplified interface"""
    return chat_send_message(message, session_id or "default")
