"""
세션 관리 및 멀티턴 대화 지원 모듈

세션별 대화 히스토리, 상태 관리, 맥락 유지를 담당
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from .utils import DEFAULT_MAX_TURNS, DEFAULT_MAX_MESSAGES
from .models import SessionContext

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """대화 턴 정보 (간소화된 버전)"""
    turn_id: str
    timestamp: datetime
    user_query: str
    ai_response: str
    category: str = ""
    product_name: str = ""
    sources: List[Dict[str, Any]] = None
    session_context: Dict[str, Any] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.sources is None:
            self.sources = []
        if self.session_context is None:
            self.session_context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "user_query": self.user_query,
            "ai_response": self.ai_response,
            "category": self.category,
            "product_name": self.product_name,
            "sources": self.sources,
            "session_context": self.session_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """딕셔너리에서 객체 생성"""
        return cls(
            turn_id=data["turn_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_query=data["user_query"],
            ai_response=data["ai_response"],
            category=data["category"],
            product_name=data["product_name"],
            sources=data["sources"],
            session_context=data["session_context"]
        )

class SessionManager:
    """세션 관리자 클래스"""
    
    def __init__(self, max_sessions: int = 1000, session_timeout: int = 3600):
        """
        Args:
            max_sessions: 최대 세션 수
            session_timeout: 세션 타임아웃 (초)
        """
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        
        # 메모리 기반 저장소 (실제 운영에서는 Redis나 DB 사용 권장)
        self._sessions: Dict[str, SessionContext] = {}
        self._conversations: Dict[str, List[ConversationTurn]] = {}
        self._message_histories: Dict[str, List[BaseMessage]] = {}
    
    def create_session(self, session_id: str = None) -> SessionContext:
        """새 세션 생성"""
        if session_id is None:
            session_id = f"session_{int(time.time())}_{hash(str(time.time())) % 10000}"
        
        # 기존 세션이 있으면 반환
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # 새 세션 생성
        now = datetime.now()
        context = SessionContext(
            session_id=session_id,
            created_at=now.isoformat(),
            last_accessed=now.isoformat(),
            last_activity=now.isoformat(),
            initial_intent="",
            session_title="",
            current_topic="",
            conversation_summary="",
            user_preferences={}
        )
        
        self._sessions[session_id] = context
        self._conversations[session_id] = []
        self._message_histories[session_id] = []
        
        logger.info(f"[SESSION] Created new session: {session_id}")
        return context
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """세션 조회"""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # 세션 타임아웃 확인
        if self._is_session_expired(session):
            self.delete_session(session_id)
            return None
        
        # 마지막 활동 시간 업데이트
        session.last_activity = datetime.now().isoformat()
        return session
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """세션 정보 업데이트"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.last_activity = datetime.now().isoformat()
        logger.info(f"[SESSION] Updated session {session_id}: {list(kwargs.keys())}")
        return True
    
    def add_conversation_turn(self, session_id: str, turn: ConversationTurn) -> bool:
        """대화 턴 추가"""
        if session_id not in self._conversations:
            return False
        
        self._conversations[session_id].append(turn)
        
        # 최대 대화 턴 수 제한 (메모리 관리) - 더 엄격한 제한
        max_turns = min(DEFAULT_MAX_TURNS, 10)  # 최대 10개 턴으로 제한
        if len(self._conversations[session_id]) > max_turns:
            self._conversations[session_id] = self._conversations[session_id][-max_turns:]
            logger.info(f"[SESSION] Trimmed conversation history to {max_turns} turns for session {session_id}")
        
        logger.info(f"[SESSION] Added turn to session {session_id}: {turn.turn_id}")
        return True
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ConversationTurn]:
        """대화 히스토리 조회 (Django에서 로드)"""
        from .utils import get_django_conversation_history
        
        # Django에서 대화 히스토리 로드
        django_history = get_django_conversation_history(session_id, limit)
        
        # Django 데이터를 ConversationTurn 객체로 변환
        turns = []
        for item in django_history:
            turn = ConversationTurn(
                turn_id=item.get("turn_id", ""),
                timestamp=datetime.fromisoformat(item.get("timestamp", datetime.now().isoformat())),
                user_query=item.get("user_query", ""),
                ai_response=item.get("ai_response", ""),
                category=item.get("category", ""),
                product_name=item.get("product_name", ""),
                sources=item.get("sources", []),
                session_context=item.get("session_context", {})
            )
            turns.append(turn)
        
        logger.info(f"📚 [SESSION] Loaded {len(turns)} conversation turns from Django for session {session_id}")
        return turns
    
    def add_message(self, session_id: str, message: BaseMessage) -> bool:
        """메시지 히스토리에 추가"""
        if session_id not in self._message_histories:
            return False
        
        self._message_histories[session_id].append(message)
        
        # 최대 메시지 수 제한
        if len(self._message_histories[session_id]) > DEFAULT_MAX_MESSAGES:
            self._message_histories[session_id] = self._message_histories[session_id][-DEFAULT_MAX_MESSAGES:]
        
        return True
    
    def get_message_history(self, session_id: str, limit: int = 20) -> List[BaseMessage]:
        """메시지 히스토리 조회"""
        if session_id not in self._message_histories:
            return []
        
        return self._message_histories[session_id][-limit:]
    
    def build_context_messages(self, session_id: str, current_query: str) -> List[BaseMessage]:
        """맥락을 고려한 메시지 리스트 생성"""
        messages = []
        session = self.get_session(session_id)
        
        if not session:
            return messages
        
        # 시스템 메시지 (세션 컨텍스트 포함)
        system_content = self._build_system_message(session)
        messages.append(SystemMessage(content=system_content))
        
        # 이전 대화 히스토리 추가
        history = self.get_message_history(session_id, limit=10)
        messages.extend(history)
        
        # 현재 질문 추가
        messages.append(HumanMessage(content=current_query))
        
        return messages
    
    def _build_system_message(self, session: SessionContext) -> str:
        """세션 컨텍스트를 포함한 시스템 메시지 생성"""
        system_parts = [
            "당신은 KB금융의 고객 상담 AI 어시스턴트입니다.",
            "다음 세션 정보를 참고하여 일관성 있는 대화를 진행하세요:"
        ]
        
        if session.session_title:
            system_parts.append(f"- 세션 주제: {session.session_title}")
        
        if session.current_topic:
            system_parts.append(f"- 현재 토픽: {session.current_topic}")
        
        if session.active_product:
            system_parts.append(f"- 활성 상품: {session.active_product}")
        
        if session.conversation_summary:
            system_parts.append(f"- 대화 요약: {session.conversation_summary}")
        
        if session.conversation_mode != "normal":
            system_parts.append(f"- 대화 모드: {session.conversation_mode}")
        
        system_parts.extend([
            "",
            "이전 대화 내용을 참고하여 자연스럽고 일관성 있는 응답을 제공하세요.",
            "사용자가 이전에 언급한 정보나 선호도를 고려하여 답변하세요."
        ])
        
        return "\n".join(system_parts)
    
    def generate_conversation_summary(self, session_id: str) -> str:
        """대화 요약 생성"""
        history = self.get_conversation_history(session_id, limit=5)
        
        if not history:
            return ""
        
        summary_parts = []
        for turn in history:
            summary_parts.append(f"Q: {turn.user_query[:50]}...")
            summary_parts.append(f"A: {turn.ai_response[:50]}...")
        
        return " | ".join(summary_parts)
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._conversations:
            del self._conversations[session_id]
        if session_id in self._message_histories:
            del self._message_histories[session_id]
        
        logger.info(f"[SESSION] Deleted session: {session_id}")
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리"""
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        logger.info(f"[SESSION] Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def _is_session_expired(self, session: SessionContext) -> bool:
        """세션 만료 여부 확인"""
        now = datetime.now()
        last_activity = datetime.fromisoformat(session.last_activity) if isinstance(session.last_activity, str) else session.last_activity
        return (now - last_activity).total_seconds() > self.session_timeout
    
    def get_session_stats(self) -> Dict[str, Any]:
        """세션 통계 정보"""
        active_sessions = len([s for s in self._sessions.values() if not self._is_session_expired(s)])
        
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": active_sessions,
            "expired_sessions": len(self._sessions) - active_sessions,
            "max_sessions": self.max_sessions,
            "session_timeout": self.session_timeout
        }

# 전역 세션 매니저 인스턴스
session_manager = SessionManager()
