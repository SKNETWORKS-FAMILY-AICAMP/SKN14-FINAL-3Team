"""
LangGraph RAG Workflow with Tool Calling (Refactored)
====================================================
리팩토링된 모듈화된 구조의 RAG 워크플로우
"""

from .agent import RAGAgent
from .graph import create_rag_workflow, create_agent, chat_send_message, api_chat
from .models import RAGState
from .tools import (
    general_faq,
    rag_search,
    product_extraction,
    product_search,
    session_summary,
    guardrail_check,
    answer,
    intent_classification,
    context_answer
)

# 전역 인스턴스
_rag_workflow = None

def get_rag_workflow() -> RAGAgent:
    """RAG 에이전트 인스턴스 반환 (싱글톤)"""
    global _rag_workflow
    if _rag_workflow is None:
        _rag_workflow = RAGAgent()
    return _rag_workflow

def get_langgraph_workflow() -> RAGAgent:
    """LangGraph 워크플로우 인스턴스 반환 (호환성 유지)"""
    return get_rag_workflow()

# ========== Export for Backward Compatibility ==========
__all__ = [
    "RAGAgent",
    "create_rag_workflow", 
    "create_agent",
    "chat_send_message",
    "api_chat",
    "RAGState",
    "general_faq", 
    "rag_search",
    "product_extraction",
    "product_search",
    "session_summary",
    "guardrail_check",
    "answer",
    "intent_classification",
    "context_answer",
    "get_rag_workflow",
    "get_langgraph_workflow"
]
