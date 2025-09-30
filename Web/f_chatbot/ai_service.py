import requests
import json
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # FastAPI 서버 설정 가져오기
        self.config = getattr(settings, 'FASTAPI_CONFIG', {})
        self.base_url = self.config.get('BASE_URL', 'http://127.0.0.1:8001')
        self.endpoints = self.config.get('ENDPOINTS', {})
        self.timeouts = self.config.get('TIMEOUTS', {})
        self.request_params = self.config.get('REQUEST_PARAMS', {})
        
        # 기본값 설정
        self.default_timeout = self.timeouts.get('DEFAULT', 60)
        self.langgraph_timeout = self.timeouts.get('LANGGRAPH', 60)
        self.health_timeout = self.timeouts.get('HEALTH_CHECK', 5)
        self.prompt_key = self.request_params.get('PROMPT_KEY', 'prompt')
    
    def check_connection(self):
        """FastAPI 서버 연결 상태 확인"""
        try:
            health_endpoint = self.endpoints.get('HEALTH', '/health')
            logger.info(f"[HEALTH] Checking connection to: {self.base_url}{health_endpoint}")
            response = requests.get(
                f"{self.base_url}{health_endpoint}",
                timeout=self.health_timeout
            )
            logger.info(f"[HEALTH] Response status: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"[HEALTH] FastAPI server is healthy")
                return True
            else:
                logger.warning(f"[HEALTH] FastAPI server returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"FastAPI 서버 연결 실패: {e}")
            return False
    
    def send_message_with_langgraph_rag(self, message, chat_id=None, chat_history=None):
        """LangGraph RAG 엔드포인트 (v2) - 툴콜링 기반"""
        try:
            # LangGraph RAG 엔드포인트 사용
            langgraph_endpoint = self.endpoints.get('LANGGRAPH_RAG', '/api/v1/langgraph/langgraph_rag')
            logger.info(f"[LANGGRAPH] Using V2 tool-calling endpoint: {langgraph_endpoint}")
            
            # 요청 데이터 구성
            request_data = {
                self.prompt_key: message
            }
            
            # session_id 추가 (V2 엔드포인트 형식)
            if chat_id:
                request_data['session_id'] = str(chat_id)
                logger.info(f"[LANGGRAPH] Sending session_id: {chat_id}")
                logger.info(f"[LANGGRAPH] Session ID type: {type(chat_id)}")
            else:
                logger.info(f"[LANGGRAPH] No session_id provided")
            
            # 대화 히스토리 전송 (LangGraph에서 컨텍스트로 사용)
            if chat_history and len(chat_history) > 0:
                request_data['chat_history'] = chat_history
                logger.info(f"[LANGGRAPH] Sending chat history: {len(chat_history)} messages")
                for i, msg in enumerate(chat_history):
                    logger.info(f"[LANGGRAPH] Message {i+1}: {msg.get('role', 'unknown')} - {msg.get('content', '')[:50]}...")
            else:
                logger.info(f"[LANGGRAPH] No chat history provided - first turn conversation")
            
            # 요청 데이터 로깅
            logger.info(f"[LANGGRAPH] Request data: {request_data}")
            logger.info(f"[LANGGRAPH] Request URL: {self.base_url}{langgraph_endpoint}")
            
            # 요청 시작 시간 기록
            start_time = time.time()
            logger.info(f"[LANGGRAPH] Request started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
            
            response = requests.post(
                f"{self.base_url}{langgraph_endpoint}",
                json=request_data,
                headers={
                    'Content-Type': 'application/json; charset=utf-8',  # charset 추가
                    'Accept': 'application/json; charset=utf-8',        # charset 추가
                    'Accept-Charset': 'utf-8'
                },
                timeout=self.langgraph_timeout
            )
            
            # 응답 시간 계산
            end_time = time.time()
            response_time = end_time - start_time
            logger.info(f"[LANGGRAPH] Response time: {response_time:.2f} seconds")
            
            # 응답 인코딩 명시적 설정
            response.encoding = 'utf-8'
            
            # 응답 상태 로깅
            logger.info(f"[LANGGRAPH] Response status: {response.status_code}")
            logger.info(f"[LANGGRAPH] Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # 응답 텍스트를 UTF-8로 디코딩
            response_text = response.text
            
            try:
                data = response.json()
                
                # 워크플로우 노드 정보 로깅
                if 'session_info' in data:
                    session_info = data['session_info']
                    logger.info(f"[LANGGRAPH] Session info: {session_info}")
                    
                    # 대화 턴 수 로깅
                    if 'conversation_turns' in session_info:
                        logger.info(f"[LANGGRAPH] Conversation turns: {session_info['conversation_turns']}")
                    
                    # 첫 번째 턴 여부 로깅
                    if 'is_first_turn' in session_info:
                        logger.info(f"[LANGGRAPH] Is first turn: {session_info['is_first_turn']}")
                
                # 응답 모드 로깅
                if 'conversation_mode' in data:
                    logger.info(f"[LANGGRAPH] Conversation mode: {data['conversation_mode']}")
                
                # 카테고리 로깅
                if 'category' in data:
                    logger.info(f"[LANGGRAPH] Category: {data['category']}")
                
                # 상품명 로깅
                if 'product_name' in data:
                    logger.info(f"[LANGGRAPH] Product name: {data['product_name']}")
                
                
                # 초기 인텐트 로깅
                if 'initial_intent' in data:
                    logger.info(f"[LANGGRAPH] Initial intent: {data['initial_intent']}")
                
                # 초기 토픽 요약 로깅
                if 'initial_topic_summary' in data:
                    logger.info(f"[LANGGRAPH] Initial topic summary: {data['initial_topic_summary']}")
                
            except json.JSONDecodeError as e:
                logger.error(f"[LANGGRAPH] JSON decode error: {e}")
                raise
            
            # LangGraph 응답 형식에 맞게 처리
            if data.get('response'):
                # AI 서버에서 보내는 응답을 일관되게 처리
                response_text = data.get('response', '').strip()
                
                # 이미 줄바꿈이 있는 경우 추가 처리하지 않음
                if response_text.count('\n') == 0:
                    # 줄바꿈이 없는 경우에만 문장 단위로 줄바꿈 추가
                    response_text = response_text.replace('다.', '다.\n')
                    response_text = response_text.replace('니다.', '니다.\n')
                    response_text = response_text.replace('요.', '요.\n')
                    response_text = response_text.replace('!', '!\n')
                    response_text = response_text.replace('?', '?\n')
                    response_text = response_text.replace('습니다.', '습니다.\n')
                    response_text = response_text.replace('입니다.', '입니다.\n')
                    
                    # 연속된 줄바꿈 정리
                    response_text = response_text.replace('\n\n\n', '\n')
                    response_text = response_text.strip()
                else:
                    # 이미 줄바꿈이 있는 경우 연속된 줄바꿈만 정리
                    response_text = response_text.replace('\n\n\n', '\n')
                    response_text = response_text.strip()
                
                # AI 서버에서 받은 실제 sources 데이터 사용
                sources_data = data.get('sources', [])
                logger.info(f"[SOURCES] FastAPI에서 받은 sources 데이터: {len(sources_data)}개")
                
                # sources가 비어있으면 다른 키들에서 메타데이터 찾기
                if not sources_data:
                    logger.info("[SOURCES] sources가 비어있어서 다른 키들에서 찾는 중...")
                    # 가능한 메타데이터 키들 확인
                    metadata_keys = ['metadata', 'documents', 'docs', 'sources', 'source']
                    for key in metadata_keys:
                        if key in data and data[key]:
                            sources_data = data[key] if isinstance(data[key], list) else [data[key]]
                            logger.info(f"[SOURCES] {key} 키에서 {len(sources_data)}개 소스 발견")
                            break
                
                # 각 소스의 구조 로깅
                for i, source in enumerate(sources_data):
                    if isinstance(source, dict):
                        logger.info(f"[SOURCES] 소스 {i+1}: file_name={source.get('file_name', 'N/A')}, file_path={source.get('file_path', 'N/A')}, page_number={source.get('page_number', 'N/A')}")
                    else:
                        logger.info(f"[SOURCES] 소스 {i+1}: {type(source)} 타입, 값={str(source)[:100]}")
                
                # RAG 검색 결과 필터링 - 관련성 높은 문서만 선택
                sources_data = self._filter_relevant_sources(sources_data, message)
                
                normalized_sources = []
                for source in sources_data:
                    if isinstance(source, dict):
                        # FastAPI의 extract_sources_from_docs 구조에 맞게 매핑
                        normalized_source = source.copy()
                        
                        # FastAPI에서 제공하는 필드들을 우선 사용
                        # file_name: FastAPI에서 직접 제공
                        if 'file_name' not in normalized_source or not normalized_source['file_name']:
                            normalized_source['file_name'] = (
                                normalized_source.get('filename', '') or 
                                normalized_source.get('source', '') or 
                                normalized_source.get('relative_path', '') or
                                'PDF 문서'
                            )
                        
                        # file_path: FastAPI에서 제공하는 경로 사용
                        if 'file_path' not in normalized_source:
                            normalized_source['file_path'] = normalized_source.get('file_path', '')
                        
                        # page_number: FastAPI에서 제공하는 페이지 번호 사용
                        if 'page_number' not in normalized_source:
                            normalized_source['page_number'] = normalized_source.get('page_number', 0)
                        
                        # page_content: FastAPI의 full_text 또는 text 사용
                        if 'page_content' not in normalized_source or not normalized_source['page_content']:
                            normalized_source['page_content'] = (
                                normalized_source.get('full_text', '') or
                                normalized_source.get('text', '') or 
                                normalized_source.get('content', '') or 
                                normalized_source.get('snippet', '') or
                                '관련 문서에서 검색된 내용입니다.'
                            )
                        
                        # text 필드도 page_content와 동일하게 설정 (호환성)
                        if 'text' not in normalized_source or not normalized_source['text']:
                            normalized_source['text'] = normalized_source['page_content']
                        
                        # relevance_score: FastAPI에서 제공하는 점수 사용
                        if 'relevance_score' in normalized_source:
                            normalized_source['score'] = normalized_source['relevance_score']
                        
                        normalized_sources.append(normalized_source)
                        logger.info(f"[SOURCES] 정규화된 소스 {len(normalized_sources)}: file_name={normalized_source.get('file_name', 'N/A')}, file_path={normalized_source.get('file_path', 'N/A')}, page_number={normalized_source.get('page_number', 'N/A')}")
                    elif isinstance(source, str):
                        # 문자열인 경우 기본 구조로 변환
                        normalized_sources.append({
                            'file_name': source,
                            'content': source,
                            'page_content': source,
                            'text': source
                        })
                    else:
                        # 기타 형태인 경우 문자열로 변환
                        normalized_sources.append({
                            'file_name': str(source),
                            'content': str(source),
                            'page_content': str(source),
                            'text': str(source)
                        })
                
                sources_data = normalized_sources
                
                # initial_topic_summary 로깅 및 처리
                initial_topic_summary = data.get('initial_topic_summary', '')
                logger.info(f"initial_topic_summary: '{initial_topic_summary}'")
                
                # initial_topic_summary가 비어있으면 session_info에서 session_title 사용
                if not initial_topic_summary or initial_topic_summary.strip() == '':
                    session_info = data.get('session_info', {})
                    session_title = session_info.get('session_title', '')
                    if session_title and session_title.strip():
                        initial_topic_summary = session_title.strip()
                        logger.info(f"Using session_title as initial_topic_summary: '{initial_topic_summary}'")
                    else:
                        # 최후의 수단: 응답에서 첫 번째 문장 추출
                        response_sentences = response_text.split('.')
                        if response_sentences and len(response_sentences[0]) > 5:
                            initial_topic_summary = response_sentences[0].strip() + '.'
                            logger.info(f"Generated initial_topic_summary from response: '{initial_topic_summary}'")    
                
                return {
                    'success': True,
                    'response': response_text,
                    'sources': sources_data,
                    'category': data.get('category', ''),
                    'product_name': data.get('product_name', ''),
                    'key_facts': data.get('key_facts', {}),
                    'session_info': data.get('session_info', {}),
                    'initial_intent': data.get('initial_intent', ''),
                    'initial_topic_summary': initial_topic_summary,  # 수정된 값 사용
                    'conversation_mode': data.get('conversation_mode', ''),
                    'current_topic': data.get('current_topic', ''),
                    'active_product': data.get('active_product', ''),
                    'experimental': True,
                    'workflow_type': 'langgraph'
                }
            else:
                return {
                    'success': False,
                    'response': data.get('response', '실험용 LangGraph RAG 처리 중 오류가 발생했습니다.'),
                    'sources': [],
                    'category': 'error',
                    'product_name': '',
                    'key_facts': {},
                    'session_info': {},
                    'initial_intent': '',
                    'initial_topic_summary': '',
                    'conversation_mode': 'error',
                    'current_topic': '',
                    'active_product': '',
                    'experimental': True,
                    'workflow_type': 'langgraph'
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"LangGraph RAG 요청 시간 초과 {self.langgraph_timeout}초)")
            return {
                'success': False,
                'response': f'실험용 LangGraph RAG 응답 시간 초과 ({self.langgraph_timeout}초).',
                'sources': [],
                'category': 'error',
                'product_name': '',
                'key_facts': {},
                'session_info': {},
                'initial_intent': '',
                'initial_topic_summary': '',
                'conversation_mode': 'timeout',
                'current_topic': '',
                'active_product': '',
                'experimental': True,
                'workflow_type': 'langgraph'
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"LangGraph RAG 연결 오류: {e}")
            return {
                'success': False,
                'response': '실험용 LangGraph RAG 서버에 연결할 수 없습니다.',
                'sources': [],
                'category': 'error',
                'product_name': '',
                'key_facts': {},
                'session_info': {},
                'initial_intent': '',
                'initial_topic_summary': '',
                'conversation_mode': 'connection_error',
                'current_topic': '',
                'active_product': '',
                'experimental': True,
                'workflow_type': 'langgraph'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"LangGraph RAG 요청 실패: {e}")
            return {
                'success': False,
                'response': f'실험용 LangGraph RAG 요청 오류: {str(e)}',
                'sources': [],
                'category': 'error',
                'product_name': '',
                'key_facts': {},
                'session_info': {},
                'initial_intent': '',
                'initial_topic_summary': '',
                'conversation_mode': 'request_error',
                'current_topic': '',
                'active_product': '',
                'experimental': True,
                'workflow_type': 'langgraph'
            }
        except Exception as e:
            logger.error(f"LangGraph RAG 예상치 못한 오류: {e}")
            return {
                'success': False,
                'response': f'실험용 LangGraph RAG 처리 중 예상치 못한 오류가 발생했습니다: {str(e)}',
                'sources': [],
                'category': 'error',
                'product_name': '',
                'key_facts': {},
                'session_info': {},
                'initial_intent': '',
                'initial_topic_summary': '',
                'conversation_mode': 'unexpected_error',
                'current_topic': '',
                'active_product': '',
                'experimental': True,
                'workflow_type': 'langgraph'
            }
    
    def get_session_info(self, session_id):
        """세션 정보 조회"""
        try:
            session_endpoint = f"/api/v1/langgraph/session/{session_id}"
            response = requests.get(
                f"{self.base_url}{session_endpoint}",
                timeout=self.default_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[SESSION] Error getting session info: {e}")
            return {
                'status': 'error',
                'message': f"세션 정보 조회 중 오류가 발생했습니다: {str(e)}"
            }
    
    def delete_session(self, session_id):
        """세션 삭제"""
        try:
            session_endpoint = f"/api/v1/langgraph/session/{session_id}"
            response = requests.delete(
                f"{self.base_url}{session_endpoint}",
                timeout=self.default_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[SESSION] Error deleting session: {e}")
            return {
                'status': 'error',
                'message': f"세션 삭제 중 오류가 발생했습니다: {str(e)}"
            }
    
    def get_session_stats(self):
        """세션 통계 조회"""
        try:
            stats_endpoint = "/api/v1/langgraph/sessions/stats"
            response = requests.get(
                f"{self.base_url}{stats_endpoint}",
                timeout=self.default_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[SESSION] Error getting session stats: {e}")
            return {
                'status': 'error',
                'message': f"세션 통계 조회 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _filter_relevant_sources(self, sources_data, query):
        """RAG 검색 결과에서 관련성 높은 문서만 필터링"""
        if not sources_data or len(sources_data) <= 1:
            return sources_data
        
        # 질의에서 핵심 키워드 추출
        import re
        query_clean = re.sub(r'\d{1,2}:\d{2}', '', query)  # 시간 정보 제거
        query_clean = re.sub(r'오전|오후', '', query_clean)
        
        # 금융 상품명 키워드 정의
        financial_products = {
            '징검다리론': ['징검다리론', '징검다리'],
            '닥터론': ['닥터론', '닥터'],
            '골든라이프': ['골든라이프', '골든', '라이프'],
            '사모사채': ['사모사채', '사모', '사채'],
            '대환대출': ['대환대출', '대환', '대출'],
            '입주자': ['입주자', '입주'],
            '주택연금': ['주택연금', '연금']
        }
        
        # 질의에서 금융 상품 키워드 찾기
        query_keywords = []
        for product, keywords in financial_products.items():
            if any(keyword in query_clean for keyword in keywords):
                query_keywords.extend(keywords)
        
        logger.info(f"[FILTER] Query keywords found: {query_keywords}")
        
        # 관련성 높은 문서 필터링
        relevant_sources = []
        for source in sources_data:
            if isinstance(source, dict):
                file_name = source.get('file_name', '').lower()
                content = source.get('page_content', '').lower()
                
                # 파일명이나 내용에 키워드가 포함된 경우
                is_relevant = any(
                    keyword.lower() in file_name or keyword.lower() in content
                    for keyword in query_keywords
                )
                
                if is_relevant:
                    relevant_sources.append(source)
                    logger.info(f"[FILTER] Relevant document found: {file_name}")
        
        # 관련 문서가 있으면 그것만 반환, 없으면 상위 2개만 반환
        if relevant_sources:
            logger.info(f"[FILTER] Filtered to {len(relevant_sources)} relevant documents")
            return relevant_sources
        else:
            logger.info(f"[FILTER] No relevant documents found, returning top 2")
            return sources_data[:2]
    
    
    # def send_message_with_intent_routing(self, message, chat_id=None):
    #     """FastAPI에 메시지 전송하고 응답 받기 (사용하지 않음)"""
    #     try:
    #         # Intent 라우팅 기반 처리 사용 (가장 적합한 엔드포인트)
    #         intent_endpoint = self.endpoints.get('INTENT_ROUTING', '/api/v1/process_with_intent_routing')
    #         response = requests.post(
    #             f"{self.base_url}{intent_endpoint}",
    #             json={
    #                 self.prompt_key: message
    #             },
    #             timeout=self.default_timeout
    #         )
    #         response.raise_for_status()
    #         
    #         data = response.json()
    #         
    #         # 응답 처리
    #         if data.get('status') == 'success':
    #             return {
    #                 'success': True,
    #                 'response': data.get('response', ''),
    #                 'sources': data.get('sources', []),
    #                 'category': data.get('category', '')
    #             }
    #         else:
    #             return {
    #                 'success': False,
    #                 'response': data.get('response', 'AI 응답 처리 중 오류가 발생했습니다.'),
    #                 'sources': [],
    #                 'category': 'error'
    #             }
    #             
    #     except requests.exceptions.Timeout:
    #         logger.error("FastAPI 서버 응답 시간 초과")
    #         return {
    #             'success': False,
    #             'response': 'AI 서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.',
    #             'sources': [],
    #             'category': 'timeout'
    #         }
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"FastAPI 통신 오류: {e}")
    #         return {
    #             'success': False,
    #             'response': 'AI 추론 서버가 연결 되어 있지 않습니다.',
    #             'sources': [],
    #             'category': 'connection_error'
    #         }
    #     except Exception as e:
    #         logger.error(f"AI 서비스 오류: {e}")
    #         return {
    #             'success': False,
    #             'response': 'AI 응답 처리 중 예상치 못한 오류가 발생했습니다.',
    #             'sources': [],
    #             'category': 'error'
    #         }
    
    # def query_rag(self, message):
    #     """RAG 질의 전용 메서드"""
    #     try:
    #         query_endpoint = self.endpoints.get('QUERY_RAG', '/api/v1/query_rag')
    #         response = requests.post(
    #             f"{self.base_url}{query_endpoint}",
    #             json={
    #                 self.prompt_key: message
    #             },
    #             timeout=self.default_timeout
    #         )
    #         response.raise_for_status()
            
    #         data = response.json()
            
    #         if data.get('status') == 'success':
    #             return {
    #                 'success': True,
    #                 'response': data.get('response', ''),
    #                 'sources': data.get('sources', [])
    #             }
    #         else:
    #             return {
    #                 'success': False,
    #                 'response': data.get('response', 'RAG 질의 처리 중 오류가 발생했습니다.'),
    #                 'sources': []
    #             }
                
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"RAG 질의 오류: {e}")
    #         return {
    #             'success': False,
    #             'response': 'AI 추론 서버가 연결 되어 있지 않습니다.',
    #             'sources': []
    #         }
