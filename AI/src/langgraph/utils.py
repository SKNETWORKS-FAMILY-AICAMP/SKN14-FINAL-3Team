"""
LangGraph 공통 유틸리티 함수들
============================
중복 코드를 제거하고 공통 기능을 제공하는 유틸리티 모듈
"""

import json
import os
import logging
import sys
import threading
import time
import yaml
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

logger = logging.getLogger(__name__)

# ========== 싱글톤 인스턴스 관리 ==========

class SLMManager:
    """SLM 인스턴스를 싱글톤으로 관리하는 클래스"""
    _instance = None
    _slm_instance = None
    _lock = threading.Lock() if threading else None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_slm(self):
        """SLM 인스턴스 반환 (필요시 생성)"""
        if self._slm_instance is None:
            # 지연 import로 순환 참조 방지
            from ..slm.slm import SLM
            self._slm_instance = SLM()
            logger.debug("SLM instance created and cached")
        return self._slm_instance


class VectorStoreManager:
    """VectorStore 인스턴스를 싱글톤으로 관리하는 클래스"""
    _instance = None
    _vector_store_instance = None
    _lock = threading.Lock() if threading else None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_vector_store(self):
        """VectorStore 인스턴스 반환 (필요시 생성)"""
        if self._vector_store_instance is None:
            # 지연 import로 순환 참조 방지
            from ..rag.vector_store import VectorStore
            self._vector_store_instance = VectorStore()
            self._vector_store_instance.get_index_ready()  # 한 번만 초기화
            logger.debug("VectorStore instance created and cached")
        return self._vector_store_instance


# 전역 매니저 인스턴스
_slm_manager = SLMManager()
_vector_store_manager = VectorStoreManager()


def get_shared_slm():
    """공유 SLM 인스턴스 가져오기"""
    return _slm_manager.get_slm()


def get_shared_vector_store():
    """공유 VectorStore 인스턴스 가져오기"""
    return _vector_store_manager.get_vector_store()


# ========== 상수 정의 ==========
DEFAULT_SEARCH_K = 3  # 검색 문서 수 감소 (속도 개선)
DEFAULT_MAX_TURNS = 20  # 대화 턴 수 감소 (속도 개선)
DEFAULT_MAX_MESSAGES = 50  # 메시지 수 감소 (속도 개선)
DEFAULT_MESSAGE_HISTORY_LIMIT = 20  # 메시지 히스토리 제한 (속도 개선)

# ========== 성능 최적화 상수 ==========
MAX_CONTEXT_LENGTH = 2000  # 컨텍스트 최대 길이
MAX_QUERY_LENGTH = 500  # 쿼리 최대 길이
CACHE_TTL_SECONDS = 300  # 캐시 TTL (5분)
MAX_CACHE_SIZE = 100  # 최대 캐시 크기
BATCH_SIZE = 5  # 배치 처리 크기

# ========== 에러 메시지 (prompts.yaml에서 로드) ==========

# ========== 프롬프트 관리 함수들 ==========

# 프롬프트 캐시 (전역 변수로 한 번만 로드)
_prompts_cache: Optional[Dict[str, Any]] = None
_cache_lock = threading.Lock() if 'threading' in sys.modules else None

def load_prompts() -> Dict[str, Any]:
    """Load prompts from YAML file with caching"""
    global _prompts_cache
    
    if _prompts_cache is not None:
        return _prompts_cache
    
    current_dir = os.path.dirname(__file__)
    prompts_path = os.path.join(current_dir, "prompts.yaml")
    
    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            _prompts_cache = yaml.safe_load(f)
            logger.debug("Prompts loaded and cached successfully")
            return _prompts_cache
    except FileNotFoundError:
        logger.warning(f"Prompts file not found: {prompts_path}")
        _prompts_cache = {}
        return _prompts_cache
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
        _prompts_cache = {}
        return _prompts_cache


def get_prompt(category: str, **kwargs) -> str:
    """
    Get formatted prompt from YAML template
    
    Args:
        category: Prompt category (supervisor, routing_prompts, etc.)
        **kwargs: Variables to format into the prompt template
        
    Returns:
        Formatted prompt string
    """
    prompts = load_prompts()
    
    # system_prompts 섹션에서 찾기
    if category in prompts.get("system_prompts", {}):
        prompt_template = prompts["system_prompts"][category]["system"]
    # routing_prompts 섹션에서 찾기
    elif category in prompts.get("routing_prompts", {}):
        prompt_template = prompts["routing_prompts"][category]
    else:
        logger.warning(f"Prompt category '{category}' not found")
        return f"프롬프트를 찾을 수 없습니다: {category}"
    
    try:
        return prompt_template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Prompt formatting error: {e}")
        return f"프롬프트 변수 오류: {e}"


def get_error_message(message_key: str, **kwargs) -> str:
    """
    Get error message with formatting
    
    Args:
        message_key: Key in error_messages section
        **kwargs: Variables to format into the message
        
    Returns:
        Formatted error message
    """
    prompts = load_prompts()
    
    if "error_messages" not in prompts:
        return "기본 에러 메시지를 불러올 수 없습니다."
    
    error_messages = prompts["error_messages"]
    
    if message_key not in error_messages:
        return "해당 에러 메시지를 찾을 수 없습니다."
    
    message_template = error_messages[message_key]
    try:
        return message_template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Error message formatting error: {e}")
        return f"에러 메시지 변수 오류: {e}"


# ========== 기존 프롬프트 템플릿 (호환성 유지) - 제거됨 ==========
# SYSTEM_PROMPTS 딕셔너리는 prompts.yaml로 이관되었습니다.
# get_prompt() 함수를 사용하여 프롬프트를 로드하세요.

def create_title_generation_prompt(query: str) -> str:
    """
    제목 생성 프롬프트 생성
    
    Args:
        query (str): 사용자 쿼리
        
    Returns:
        str: 제목 생성을 위한 프롬프트
    """
    return f"""당신은 '챗봇 세션 제목 생성기'입니다. 사용자의 질문을 보고 
        이 세션을 대표할 매우 간결한 한 줄 제목을 생성하세요.

        사용자 질문: {query}

        출력: 제목 텍스트만 한 줄로 출력
        - 한국어로 간결하게 (반드시 15자 이하)
        - 불필요한 설명 없이 제목만 반환
        - 예시: '햇살론 문의', '대출 문의', '상품 안내'
        - 중요: 15자를 초과하면 안됩니다!"""


def truncate_title(title: str, max_length: int = 15) -> str:
    """
    제목을 지정된 길이로 자르기
    
    Args:
        title (str): 원본 제목
        max_length (int): 최대 길이 (기본값: 15)
        
    Returns:
        str: 잘린 제목
    """
    if len(title) > max_length:
        return title[:max_length].rstrip()
    return title


def generate_session_title(query: str, slm_instance) -> str:
    """
    세션 제목 생성 (완전한 로직)
    
    Args:
        query (str): 사용자 쿼리
        slm_instance: SLM 인스턴스
        
    Returns:
        str: 생성된 세션 제목
    """
    try:
        # LLM으로 제목 생성
        title_prompt = create_title_generation_prompt(query)
        logger.info(f"Title generation prompt: {title_prompt}")
        
        raw_title = (slm_instance.invoke(title_prompt) or "").strip()
        logger.info(f"Raw title from LLM: '{raw_title}'")
        
        if raw_title:
            session_title = raw_title.splitlines()[0].strip()
            # 15자 제한 강제 적용
            session_title = truncate_title(session_title, 15)
            logger.info(f"Final session title: '{session_title}'")
            return session_title
        else:
            # LLM 실패시 폴백
            fallback_title = truncate_title(query, 15)
            logger.info(f"LLM failed, using fallback title: '{fallback_title}'")
            return fallback_title
            
    except Exception as e:
        # 에러 발생시 폴백
        fallback_title = truncate_title(query, 15)
        logger.error(f"Title generation error: {e}, using fallback: '{fallback_title}'")
        return fallback_title


def format_context(documents: List[Document]) -> str:
    """
    문서들을 컨텍스트 형식으로 포맷팅 (성능 최적화)
    
    Args:
        documents: Document 리스트
        
    Returns:
        str: 포맷팅된 컨텍스트 문자열
    """
    lines = []
    current_length = 0
    
    for i, doc in enumerate(documents, 1):
        if current_length >= MAX_CONTEXT_LENGTH:
            break
            
        src = doc.metadata.get("source", f"document_{i}") if doc.metadata else f"document_{i}"
        snippet = doc.page_content.strip()
        if not snippet:
            continue
        
        # 각 문서의 내용을 500자로 제한
        if len(snippet) > 500:
            snippet = snippet[:500] + "..."
        
        line = f"[source: {src}]\n{snippet}"
        lines.append(line)
        current_length += len(line) + 5  # "\n---\n" 길이 고려
    
    return "\n---\n".join(lines)


def extract_sources_from_docs(documents: List[Document]) -> List[Dict[str, Any]]:
    """
    문서들에서 소스 정보 추출 (프론트엔드 표시용)
    
    Args:
        documents: Document 리스트
        
    Returns:
        List[Dict]: 소스 정보 리스트 (프론트엔드 친화적 구조)
    """
    sources = []
    for i, doc in enumerate(documents):
        metadata = doc.metadata or {}
        
        # 프론트엔드에서 표시하기 쉬운 구조로 변환
        source_info = {
            'id': i + 1,  # 소스 ID
            'file_name': metadata.get('file_name', 'Unknown'),  # PDF 파일명
            'file_path': metadata.get('file_path', ''),  # 파일 경로
            'page_number': metadata.get('page_number', 0),  # 페이지 번호
            'main_category': metadata.get('main_category', ''),  # 메인 카테고리
            'sub_category': metadata.get('sub_category', ''),  # 서브 카테고리
            'text': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,  # 내용 미리보기
            'full_text': doc.page_content,  # 전체 내용
            'relevance_score': getattr(doc, 'score', 0.0) if hasattr(doc, 'score') else 0.0,  # 관련도 점수
        }
        
        # 원본 메타데이터도 보존 (필요시 사용)
        source_info['metadata'] = metadata
        
        sources.append(source_info)
    
    logger.debug(f"📄 [SOURCES] 추출된 소스 정보: {len(sources)}개")
    
    return sources


def create_rag_response(slm_instance, query: str, documents: List[Document]) -> tuple[str, List[Dict[str, Any]]]:
    """
    RAG 검색 결과로부터 응답 생성
    
    Args:
        slm_instance: SLM 인스턴스
        query: 사용자 쿼리
        documents: 검색된 문서들
        
    Returns:
        tuple: (응답 텍스트, 소스 정보 리스트)
    """
    if not documents:
        return get_error_message("no_documents"), []
    
    # 컨텍스트 생성
    context_text = format_context(documents)
    
    # LLM으로 응답 생성
    system_prompt = get_prompt("rag_system", context_text=context_text)
    messages = [HumanMessage(content=system_prompt), HumanMessage(content=query)]
    response = slm_instance.invoke(messages)
    
    # 소스 정보 추출
    sources = extract_sources_from_docs(documents)
    
    return response, sources


def create_simple_response(slm_instance, query: str, prompt_type: str) -> str:
    """
    간단한 프롬프트로 응답 생성
    
    Args:
        slm_instance: SLM 인스턴스
        query: 사용자 쿼리
        prompt_type: 프롬프트 타입 (faq_system 등)
        
    Returns:
        str: 생성된 응답
    """
    try:
        # prompt_type을 그대로 사용 (YAML 키와 매치)
        prompt = get_prompt(prompt_type, query=query)
        return slm_instance.invoke(prompt)
    except Exception:
        return get_error_message(f"{prompt_type.replace('_system', '_error')}")


def trim_message_history(messages: List[BaseMessage], max_messages: int = DEFAULT_MESSAGE_HISTORY_LIMIT) -> List[BaseMessage]:
    """
    메시지 히스토리를 제한하여 메모리 누수 방지
    
    Args:
        messages: 메시지 리스트
        max_messages: 최대 메시지 수 (기본값: 50)
        
    Returns:
        제한된 메시지 리스트 (최신 메시지들만 유지)
    """
    if len(messages) <= max_messages:
        return messages
        
    # 최신 메시지들만 유지
    trimmed_messages = messages[-max_messages:]
    logger.info(f"Message history trimmed: {len(messages)} -> {len(trimmed_messages)}")
    return trimmed_messages


def create_guardrail_response(slm_instance, response: str) -> tuple[str, List[str]]:
    """
    가드레일 검사 및 응답 생성
    
    Args:
        slm_instance: SLM 인스턴스
        response: 검사할 응답
        
    Returns:
        tuple: (준수 응답, 위반 사항 리스트)
    """
    try:
        # 가드레일 비활성화 옵션 (환경변수로 제어)
        import os
        if os.getenv("DISABLE_GUARDRAIL", "false").lower() == "true":
            logger.info("🛡️ [GUARDRAIL] Disabled by environment variable")
            return response, []
        
        logger.info("🛡️ [GUARDRAIL] Loading config...")
        # YAML 정책 기반 가드레일 검사
        guardrail_config = load_guardrail_config()
        logger.info("🛡️ [GUARDRAIL] Config loaded")
        
        # 기본 응답
        compliant_response = response
        violations = []
        
        # 품질 검사 (빠른 체크 우선)
        logger.info("🛡️ [GUARDRAIL] Checking completeness...")
        if guardrail_config.get("quality", {}).get("completeness_check", {}).get("enabled", False):
            violations.extend(check_completeness(response, guardrail_config))
        
        # 정확성 검사 (더 복잡한 검사)
        logger.info("🛡️ [GUARDRAIL] Checking accuracy...")
        if guardrail_config.get("quality", {}).get("accuracy_check", {}).get("enabled", False):
            violations.extend(check_accuracy(response, guardrail_config))
        
        # 용어 정규화 (캐싱 적용)
        logger.info("🛡️ [GUARDRAIL] Normalizing terminology...")
        if guardrail_config.get("terminology", {}).get("normalization", {}).get("enabled", False):
            compliant_response = normalize_terminology(compliant_response, guardrail_config)
        
        # 구조 검사 (선택적)
        logger.info("🛡️ [GUARDRAIL] Applying emphasis...")
        if guardrail_config.get("structure", {}).get("emphasis", {}).get("enabled", False):
            compliant_response = apply_emphasis(compliant_response, guardrail_config)
        
        # 위반이 있는 경우 안전한 응답으로 대체
        if violations:
            logger.warning(f"🛡️ [GUARDRAIL] Found {len(violations)} violations")
            compliant_response = "죄송합니다. 해당 질문에 대해서는 정확한 답변을 드리기 어렵습니다. 관련 부서에 문의해주세요."
        
        logger.info("🛡️ [GUARDRAIL] Guardrail check completed")
        return compliant_response, violations
        
    except Exception as e:
        logger.error(f"🛡️ [GUARDRAIL] Error: {e}")
        return get_error_message("guardrail_error"), ["가드레일 검사 오류"]


# 전역 캐시 변수
_guardrail_config_cache = None
_glossary_terms_cache = None
_search_cache = {}  # 검색 결과 캐싱
_conversation_history_cache = {}  # 대화 히스토리 캐싱

def get_cached_search_result(query: str, product_name: str = "") -> Optional[List[Document]]:
    """검색 결과 캐시에서 가져오기 (TTL 체크 포함)"""
    cache_key = f"{query}:{product_name}"
    if cache_key in _search_cache:
        cache_entry = _search_cache[cache_key]
        # TTL 체크
        if time.time() - cache_entry.get("timestamp", 0) < CACHE_TTL_SECONDS:
            return cache_entry.get("documents")
        else:
            # 만료된 캐시 제거
            del _search_cache[cache_key]
    return None

def set_cached_search_result(query: str, product_name: str, documents: List[Document]) -> None:
    """검색 결과 캐시에 저장 (TTL 포함)"""
    cache_key = f"{query}:{product_name}"
    _search_cache[cache_key] = {
        "documents": documents,
        "timestamp": time.time()
    }
    # 캐시 크기 제한 (메모리 누수 방지)
    if len(_search_cache) > MAX_CACHE_SIZE:
        # LRU 방식으로 가장 오래된 항목 제거
        oldest_key = min(_search_cache.keys(), 
                        key=lambda k: _search_cache[k].get("timestamp", 0))
        del _search_cache[oldest_key]

def get_django_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Django에서 대화 히스토리를 로드하는 함수 (캐싱 + 성능 최적화)
    
    Args:
        session_id: 세션 ID
        limit: 최대 로드할 대화 수
        
    Returns:
        대화 히스토리 리스트
    """
    global _conversation_history_cache
    
    # 캐시에서 확인
    cache_key = f"history_{session_id}_{limit}"
    if cache_key in _conversation_history_cache:
        logger.info(f"📚 [HISTORY] Using cached conversation history for session {session_id}")
        return _conversation_history_cache[cache_key]
    
    try:
        # Django에서 대화 히스토리 로드 (실제 구현은 Django API 호출)
        logger.info(f"📚 [HISTORY] Loading conversation history from Django for session {session_id}")
        
        # TODO: 실제 Django API 호출 구현
        # 예시: 
        # import requests
        # response = requests.get(f"/api/conversation-history/{session_id}?limit={limit}")
        # history = response.json()
        
        # 임시로 빈 리스트 (실제 구현 시 Django API 호출)
        history = []
        
        # 캐시에 저장 (TTL: 5분)
        _conversation_history_cache[cache_key] = {
            "data": history,
            "timestamp": time.time()
        }
        
        # 캐시 크기 제한 (메모리 효율성)
        if len(_conversation_history_cache) > 50:
            # 가장 오래된 항목 제거
            oldest_key = min(_conversation_history_cache.keys(), 
                           key=lambda k: _conversation_history_cache[k].get("timestamp", 0))
            del _conversation_history_cache[oldest_key]
        
        return history
        
    except Exception as e:
        logger.error(f"📚 [HISTORY] Failed to load conversation history: {e}")
        return []

def clear_conversation_history_cache(session_id: str = None) -> None:
    """대화 히스토리 캐시 클리어"""
    global _conversation_history_cache
    
    if session_id:
        # 특정 세션 캐시만 클리어
        keys_to_remove = [key for key in _conversation_history_cache.keys() if f"history_{session_id}_" in key]
        for key in keys_to_remove:
            del _conversation_history_cache[key]
        logger.info(f"📚 [HISTORY] Cleared cache for session {session_id}")
    else:
        # 전체 캐시 클리어
        _conversation_history_cache.clear()
        logger.info("📚 [HISTORY] Cleared all conversation history cache")

def load_guardrail_config() -> Dict[str, Any]:
    """가드레일 YAML 설정 로드 (캐싱 적용)"""
    global _guardrail_config_cache
    
    if _guardrail_config_cache is not None:
        return _guardrail_config_cache
    
    try:
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, "guardrails", "policy_rules.yaml")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            _guardrail_config_cache = yaml.safe_load(f)
            return _guardrail_config_cache
    except Exception as e:
        logger.error(f"Failed to load guardrail config: {e}")
        return {}


def check_accuracy(response: str, config: Dict[str, Any]) -> List[str]:
    """정확성 검사"""
    violations = []
    accuracy_config = config.get("quality", {}).get("accuracy_check", {})
    
    if not accuracy_config.get("enabled", False):
        return violations
    
    # 키워드 기반 검사
    triggers = accuracy_config.get("triggers", {})
    keywords = triggers.get("keywords", [])
    
    # 컨텍스트 감지 설정
    context_detection = accuracy_config.get("context_detection", {})
    product_indicators = context_detection.get("product_indicators", [])
    banking_terms = context_detection.get("banking_terms", [])
    
    for keyword in keywords:
        if keyword in response:
            # 상품 설명 컨텍스트가 있는지 확인
            has_product_context = any(indicator in response for indicator in product_indicators)
            has_banking_context = any(term in response for term in banking_terms)
            
            if has_product_context or has_banking_context:
                logger.info(f"🛡️ [GUARDRAIL] Trigger keyword '{keyword}' found but product/banking context detected - allowing")
                continue
                
            logger.warning(f"🛡️ [GUARDRAIL] Found trigger keyword: '{keyword}' in response")
            violations.append(f"검증이 필요한 키워드 포함: {keyword}")
    
    return violations


def check_completeness(response: str, config: Dict[str, Any]) -> List[str]:
    """완전성 검사"""
    violations = []
    completeness_config = config.get("quality", {}).get("completeness_check", {})
    
    if not completeness_config.get("enabled", False):
        return violations
    
    # 기본적인 완전성 검사
    if len(response.strip()) < 50:
        violations.append("응답이 너무 짧습니다")
    
    return violations


def normalize_terminology(response: str, config: Dict[str, Any]) -> str:
    """용어 정규화 (캐싱 적용)"""
    global _glossary_terms_cache
    
    try:
        # 캐시에서 로드
        if _glossary_terms_cache is None:
            current_dir = os.path.dirname(__file__)
            glossary_path = os.path.join(current_dir, "guardrails", "glossary_terms.yaml")
            
            with open(glossary_path, 'r', encoding='utf-8') as f:
                _glossary_terms_cache = yaml.safe_load(f)
        
        # 용어 치환
        terms = _glossary_terms_cache.get("terms", [])
        for term in terms:
            from_term = term.get("from", "")
            to_term = term.get("to", "")
            if from_term and to_term:
                response = response.replace(from_term, to_term)
        
        return response
    except Exception as e:
        logger.error(f"Terminology normalization failed: {e}")
        return response


def apply_emphasis(response: str, config: Dict[str, Any]) -> str:
    """강조 적용"""
    emphasis_config = config.get("structure", {}).get("emphasis", {})
    
    if not emphasis_config.get("enabled", False):
        return response
    
    # 기본적인 강조 적용 (실제로는 더 복잡한 로직 필요)
    priority_keywords = emphasis_config.get("priority_keywords", {})
    
    for keyword, priority in priority_keywords.items():
        if keyword in response and priority >= 3:
            # 중요 키워드 강조 (실제 구현에서는 더 정교한 처리 필요)
            pass
    
    return response


def extract_product_name(slm_instance, query: str) -> str:
    """
    상품명 추출 (새로운 프롬프트 시스템 사용)
    
    Args:
        slm_instance: SLM 인스턴스
        query: 사용자 쿼리
        
    Returns:
        str: 추출된 상품명
    """
    try:
        # 새로운 프롬프트 시스템 사용
        prompt = get_prompt("product_extraction", query=query)
        extracted_product = slm_instance.invoke(prompt).strip()
        
        # 대괄호 제거 및 정리
        if extracted_product.startswith('[') and extracted_product.endswith(']'):
            extracted_product = extracted_product[1:-1].strip()
        
        return extracted_product
        
    except Exception as e:
        logger.error(f"Product extraction failed: {e}")
        return "일반"


def classify_product_subcategory(product_name: str) -> str:
    """
    상품명을 기반으로 서브 카테고리 분류
    
    Args:
        product_name: 추출된 상품명
        
    Returns:
        str: 서브 카테고리
    """
    from .models import LoanSubType, DepositSubType, CardSubType, SavingsSubType
    
    product_lower = product_name.lower()
    
    # 대출 상품 분류
    if any(keyword in product_lower for keyword in ["햇살론", "닥터론", "로이어론"]):
        return LoanSubType.PERSONAL_CREDIT.value
    elif any(keyword in product_lower for keyword in ["내집마련", "입주자", "대환"]):
        return LoanSubType.PERSONAL_HOUSING_FUND.value
    elif any(keyword in product_lower for keyword in ["버팀목", "전세"]):
        return LoanSubType.PERSONAL_SECURED_JEONSE.value
    elif any(keyword in product_lower for keyword in ["매직카", "자동차"]):
        return LoanSubType.PERSONAL_AUTO.value
    elif any(keyword in product_lower for keyword in ["군인", "폐업", "기업"]):
        return LoanSubType.BUSINESS_LOAN.value
    
    # 예금/적금 상품 분류
    elif any(keyword in product_lower for keyword in ["예금", "정기예금"]):
        return DepositSubType.TIME_DEPOSIT.value
    elif any(keyword in product_lower for keyword in ["적금", "정기적금"]):
        return SavingsSubType.REGULAR_SAVINGS.value
    elif any(keyword in product_lower for keyword in ["자유적금"]):
        return SavingsSubType.FREE_SAVINGS.value
    elif any(keyword in product_lower for keyword in ["주택청약"]):
        return SavingsSubType.HOUSING_SAVINGS.value
    
    # 카드 상품 분류
    elif any(keyword in product_lower for keyword in ["카드", "신용카드"]):
        return CardSubType.CREDIT_CARD.value
    elif any(keyword in product_lower for keyword in ["체크카드"]):
        return CardSubType.DEBIT_CARD.value
    
    # 기본값
    else:
        return "일반"


def create_supervisor_prompt(query: str) -> str:
    """
    슈퍼바이저 프롬프트 생성 (새로운 3가지 노드 워크플로우용)
    
    Args:
        query: 사용자 쿼리
        
    Returns:
        str: 슈퍼바이저 프롬프트
    """
    try:
        return get_prompt("supervisor", query=query)
    except KeyError as e:
        logger.error(f"Prompt formatting error: {e}")
        # 폴백 프롬프트 사용
        return f"""당신은 KB금융그룹의 중앙 관리자입니다. 사용자의 질문을 분석하여 적절한 노드를 선택하세요.
        
        사용자 질문: {query}
        
        사용 가능한 노드:
        - answer: 최종 답변 생성
        - rag_search: 문서 검색이 필요한 질문
        - product_extraction: 상품명 추출이 필요한 질문
        
        적절한 노드를 선택하고 reasoning을 제공하세요."""

def create_error_response(error_type: str, **kwargs) -> Dict[str, Any]:
    """
    에러 응답 생성
    
    Args:
        error_type: 에러 타입
        **kwargs: 추가 파라미터
        
    Returns:
        Dict: 에러 응답 딕셔너리
    """
    return {
        "response": get_error_message(error_type),
        "sources": kwargs.get("sources", []),
        "ready_to_answer": True
    }


# ========== 성능 최적화 유틸리티 함수들 ==========

def optimize_query_length(query: str, max_length: int = MAX_QUERY_LENGTH) -> str:
    """쿼리 길이 최적화"""
    if len(query) > max_length:
        return query[:max_length].rsplit(' ', 1)[0] + "..."
    return query


def batch_process_items(items: List[Any], batch_size: int = BATCH_SIZE) -> List[List[Any]]:
    """배치 처리로 메모리 효율성 향상"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def cleanup_expired_cache():
    """만료된 캐시 정리"""
    global _search_cache, _conversation_history_cache
    current_time = time.time()
    
    # 검색 캐시 정리
    expired_keys = []
    for key, value in _search_cache.items():
        if current_time - value.get("timestamp", 0) > CACHE_TTL_SECONDS:
            expired_keys.append(key)
    
    for key in expired_keys:
        del _search_cache[key]
    
    # 대화 히스토리 캐시 정리
    expired_history_keys = []
    for key, value in _conversation_history_cache.items():
        if current_time - value.get("timestamp", 0) > CACHE_TTL_SECONDS:
            expired_history_keys.append(key)
    
    for key in expired_history_keys:
        del _conversation_history_cache[key]
    
    if expired_keys or expired_history_keys:
        logger.info(f"🧹 [CACHE] Cleaned up {len(expired_keys)} search cache and {len(expired_history_keys)} history cache entries")


def get_memory_usage() -> Dict[str, Any]:
    """메모리 사용량 모니터링"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss_mb": memory_info.rss / 1024 / 1024,  # 실제 메모리 사용량
        "vms_mb": memory_info.vms / 1024 / 1024,  # 가상 메모리 사용량
        "cache_size": len(_search_cache),
        "history_cache_size": len(_conversation_history_cache)
    }
