"""
KB금융그룹 RAG Agent - Agent Implementation
==========================================
Unified entry point for RAG agent with proper error handling
and state management.
"""

from typing import Dict, Any, Optional, List, Iterator
import logging
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from .models import RAGState, APIResponse, ErrorResponse, WorkflowConfig, SessionConfig
from .graph import create_rag_workflow
from .session_manager import session_manager
from .utils import generate_session_title, trim_message_history, get_shared_slm, get_shared_vector_store
from ..slm.slm import SLM
from ..rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Main class for KB금융그룹 RAG agent
    
    Provides unified interface for RAG-based financial consultation with conversation
    management, state persistence, and proper error handling.
    """
    
    def __init__(self, checkpointer: BaseCheckpointSaver | None = None, config: WorkflowConfig | None = None) -> None:
        """
        Initialize the agent with workflow and dependencies
        
        Args:
            checkpointer: Checkpoint saver for conversation persistence
            config: Workflow configuration
        """
        self.checkpointer = checkpointer or MemorySaver()
        self.config = config or WorkflowConfig()
        # 싱글톤 인스턴스 사용으로 메모리 효율성 증대
        self.slm = get_shared_slm()
        self.vector_store = get_shared_vector_store()
        self.workflow = create_rag_workflow(
            checkpointer=self.checkpointer, 
            llm=self.slm.llm
        )
        logger.info("RAGAgent initialized")
    
    def chat(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        stream: bool = False,
        language: str = "ko",
        chat_history: List[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any] | Iterator[Dict[str, Any]]:
        """
        Unified chat method using continuous workflow
        
        Args:
            message: User input message
            session_id: Session identifier for conversation persistence  
            stream: Whether to stream response chunks
            language: Language code for response (default: "ko")
            chat_history: Django에서 전달받은 대화 히스토리
            **kwargs: Additional configuration options
            
        Returns:
            Response dict for sync mode, Iterator for stream mode
        """
        try:
            # Prepare configuration
            config = {
                "configurable": {
                    "thread_id": session_id or "default",
                    "language": language,
                    **kwargs
                }
            }
            
            # Django에서 전달받은 대화 히스토리를 메시지로 변환 (성능 최적화)
            messages = []
            if chat_history:
                # 최근 10개 메시지만 처리 (성능 최적화)
                recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
                logger.info(f"[AGENT] Processing {len(recent_history)} messages from Django chat history (total: {len(chat_history)})")
                
                for msg in recent_history:
                    if msg.get('role') == 'user':
                        messages.append(HumanMessage(content=msg.get('content', '')))
                    elif msg.get('role') == 'assistant':
                        messages.append(AIMessage(content=msg.get('content', '')))
                logger.info(f"[AGENT] Converted {len(messages)} messages from Django history")
            
            # 현재 메시지 추가
            messages.append(HumanMessage(content=message))
            
            # Prepare input data
            input_data = {
                "query": message,
                "session_id": session_id,
                "language": language,
                "messages": messages,  # Django 히스토리 + 현재 메시지
                "conversation_history": chat_history or [],  # Django 히스토리 원본
                # Initialize state flags
                "ready_to_answer": False,
                "needs_clarification": False,
                "query_complete": False,
                "n_tool_calling": 0,
                "retry_count": 0,
                # Initialize execution path tracking
                "execution_path": []
            }
            
            logger.info(f"Processing chat request: session={session_id}, stream={stream}")
            
            if stream:
                return self._stream_execution(input_data, config)
            else:
                return self._execute_with_interrupt_handling(input_data, config)
                
        except Exception as e:
            logger.error(f"Chat execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "error": f"Agent execution failed: {str(e)}",
                "session_id": session_id
            }
    
    def _execute_with_interrupt_handling(
        self, 
        input_data: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute workflow with interrupt handling for web frontends
        
        Args:
            input_data: Prepared input data for workflow
            config: Configuration including thread_id and language
            
        Returns:
            Structured response dict with success status and results
        """
        try:
            logger.debug("Executing workflow with interrupt handling")
            logger.info("[WORKFLOW] Starting workflow execution...")
            result = self.workflow.invoke(input_data, config=config)
            
            # 워크플로우 실행 완료
            logger.info("[WORKFLOW] Execution completed successfully")
            
            # Extract response message for presentation
            response_message = result.get("response", "") if isinstance(result, dict) else ""
            
            # Check for clarification needs
            if result.get("needs_clarification") and result.get("clarification_question"):
                return {
                    "success": True,
                    "status": "needs_clarification",
                    "clarification_question": result.get("clarification_question"),
                    "session_id": result.get("session_id"),
                    "messages": result.get("messages", []),
                    "response": response_message,
                    "next_action": "provide_clarification"
                }
            
            # Check for errors
            if result.get("error_message"):
                return {
                    "success": False,
                    "status": "error",
                    "error": result.get("error_message"),
                    "session_id": result.get("session_id"),
                    "messages": result.get("messages", []),
                    "response": response_message
                }
            
            # Normal completion
            session_title = result.get("session_title", "")
            # session_context에서도 session_title 가져오기 (fallback)
            session_context = result.get("session_context")
            if not session_title and session_context:
                session_title = getattr(session_context, 'session_title', '')
            
            logger.info(f"Final result session_title: '{session_title}'")
            return {
                "success": True,
                "status": "completed",
                "response": response_message,
                "messages": result.get("messages", []),
                "sources": result.get("sources", []),
                "category": result.get("category", ""),
                "product_name": result.get("product_name", ""),
                "session_info": result.get("session_info", {}),
                "initial_intent": result.get("initial_intent", ""),
                "initial_topic_summary": session_title,
                "conversation_mode": result.get("conversation_mode", "tool_calling"),
                "current_topic": result.get("current_topic", ""),
                "active_product": result.get("active_product", ""),
                "ready_to_answer": result.get("ready_to_answer", True),
                "n_tool_calling": result.get("n_tool_calling", 0)
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "error": f"LangGraph V2 RAG 처리 중 오류가 발생했습니다: {str(e)}",
                "session_id": input_data.get("session_id"),
                "response": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
                "messages": [],
                "sources": []
            }
    
    def _stream_execution(
        self, 
        input_data: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """
        Streaming execution for workflow
        
        Args:
            input_data: Prepared input data for workflow
            config: Configuration including thread_id and language
            
        Yields:
            Raw streaming chunks from workflow execution
        """
        try:
            logger.debug("Starting streaming execution")
            for chunk in self.workflow.stream(input_data, config=config):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming execution failed: {e}", exc_info=True)
            yield {"error": f"Streaming failed: {str(e)}"}
    
    def get_conversation_history(self, session_id: str) -> List[Any]:
        """
        Retrieve conversation history for given session with memory limit
        
        Args:
            session_id: Session identifier for conversation
            
        Returns:
            List of messages from conversation history (limited to prevent memory issues)
        """
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = self.workflow.get_state(config)
            messages = state.values.get("messages", []) if state.values else []
            
            # 메시지 히스토리 제한 적용
            trimmed_messages = trim_message_history(messages)
            logger.debug(f"Retrieved {len(trimmed_messages)} messages for session {session_id} (original: {len(messages)})")
            return trimmed_messages
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}", exc_info=True)
            return []
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear conversation history for given session
        
        Args:
            session_id: Session identifier for conversation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Conversation cleared for session: {session_id}")
            # Note: Implementation depends on checkpointer type
            return True
        except Exception as e:
            logger.error(f"Failed to clear conversation: {e}", exc_info=True)
            return False
    
    def run_workflow(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility
        
        Args:
            query: User query
            session_id: Session identifier
            
        Returns:
            Workflow execution result
        """
        return self.chat(query, session_id)
    
    def send_message_with_langgraph_rag(self, message: str, session_id: str, chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Django에서 호출하는 함수 - 대화 히스토리 지원
        
        Args:
            message: 사용자 메시지
            session_id: 세션 ID
            chat_history: Django에서 전달받은 대화 히스토리
            
        Returns:
            LangGraph 실행 결과
        """
        try:
            result = self.chat(message, session_id, chat_history=chat_history)
            
            # Django에서 필요한 형태로 변환
            return {
                "response": result.get("response", ""),
                "sources": result.get("sources", []),
                "category": result.get("category", ""),
                "product_name": result.get("product_name", ""),
                "session_id": session_id,
                "success": result.get("success", True)
            }
        except Exception as e:
            logger.error(f"Django integration failed: {e}")
            return {
                "response": f"처리 중 오류가 발생했습니다: {str(e)}",
                "sources": [],
                "category": "",
                "product_name": "",
                "session_id": session_id,
                "success": False
            }


# ========== Factory Functions ==========

def create_agent(checkpointer: BaseCheckpointSaver | None = None, config: WorkflowConfig | None = None) -> RAGAgent:
    """
    Create agent instance with optional checkpointer and config
    
    Args:
        checkpointer: Optional checkpoint saver for conversation persistence
        config: Optional workflow configuration
        
    Returns:
        Configured RAGAgent instance
    """
    return RAGAgent(checkpointer, config)


# ========== Unified Chat Interface Functions ==========

def chat_send_message(message: str, session_id: str, **kwargs) -> Dict[str, Any]:
    """
    Send message in chat - unified interface for all chat interactions
    
    Args:
        message: User input message
        session_id: Session identifier for conversation
        **kwargs: Additional configuration options
        
    Returns:
        Response dict with success status and results
    """
    agent = create_agent()
    return agent.chat(message, session_id, **kwargs)


def chat_get_history(session_id: str) -> List[Dict[str, str]]:
    """
    Get chat message history in format suitable for chat UI
    
    Args:
        session_id: Session identifier for conversation
        
    Returns:
        List of formatted message dictionaries
    """
    agent = create_agent()
    messages = agent.get_conversation_history(session_id)
    
    chat_history = []
    for msg in messages:
        if hasattr(msg, 'content'):
            role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
            chat_history.append({
                "role": role,
                "content": msg.content,
                "timestamp": getattr(msg, 'timestamp', None)
            })
    
    return chat_history


def chat_stream_message(message: str, session_id: str, **kwargs) -> Iterator[Dict[str, Any]]:
    """
    Stream chat response yielding chunks as they come
    
    Args:
        message: User input message
        session_id: Session identifier for conversation
        **kwargs: Additional configuration options
        
    Yields:
        Streaming response chunks
    """
    agent = create_agent()
    for chunk in agent.chat(message, session_id, stream=True, **kwargs):
        yield chunk


def api_chat(message: str, session_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    API method for web frontends - unified chat interface
    
    Args:
        message: User input message
        session_id: Optional session identifier for conversation
        **kwargs: Additional configuration options
        
    Returns:
        Response dict with success status and results
    """
    agent = create_agent()
    return agent.chat(message, session_id, **kwargs)
