from typing import Literal, List, Optional, Dict, Any
import logging
import anyio
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
import os

from src.orchestrator import Orchestrator
from src.langgraph.langgraph_v2 import get_langgraph_workflow
from src.rag.vector_store import VectorStore
from src.config import VECTOR_STORE_INDEX_NAME, DATA_FOLDER_PATH
from src.constants import STATUS_SUCCESS, STATUS_FAIL

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# ==============================================
# Pydantic 모델 정의 (Request/Response)
# ==============================================

# 기본 응답 모델
# RAG, Sub/Main 파이프라인, 데이터 관리 등 기본 응답 모델
class BaseResponse(BaseModel):
    status: Literal[STATUS_SUCCESS, STATUS_FAIL]

# 요청 모델들
# RAG 질의 요청 모델
class QueryRagInput(BaseModel):
    prompt: str

# 기존 워크플로우 실행 요청 모델
class LLMOnlyInput(BaseModel):
    prompt: str

# Intent 라우팅 기반 처리 요청 모델
class IntentRoutingInput(BaseModel):
    prompt: str

# LangGraph RAG 요청 모델 (세션 지원)
class LangGraphRAGInput(BaseModel):
    prompt: str
    session_id: Optional[str] = None  # 세션 ID (선택사항)
    chat_history: Optional[List[Dict[str, Any]]] = None  # Django에서 전달받은 대화 히스토리

# 폴더 업로드 요청 모델
class IngestFolderReq(BaseModel):
    # ALLOWED_ROOT 기준 "상대 폴더 경로"만 받습니다. (예: "법률률", "branch_docs/여신")
    root_folder_path: str = Field(..., min_length=1, description="ALLOWED_ROOT-relative folder path")

# 벡터 삭제 요청 모델
class DeleteVectorsByConditionReq(BaseModel):
    field: str = Field(..., description="삭제할 메타데이터 필드명 (예: main_category, sub_category, file_name)")
    value: str = Field(..., description="삭제할 값 (예: 법률, 개인 신용대출, 특정파일.pdf)")

# Sub/Main 라우터 요청 모델
class IntentRouterInput(BaseModel):
    question: str

# 응답 모델들
# RAG 질의 응답 모델
class QueryRagResponse(BaseResponse):
    response: str
    sources: Optional[List[Dict]] = None  

# 기존 워크플로우 실행 응답 모델
class LLMOnlyResponse(BaseResponse):
    response: str

# Intent 라우팅 기반 처리 응답 모델
class IntentRoutingResponse(BaseResponse):
    response: str
    sources: Optional[List[Dict]] = []
    category: Optional[str] = ""

# 개별 파일 업로드 응답 모델
class UploadRagDocsResponse(BaseResponse):
    chunk_ids: List[str]
    message: str



# 벡터 삭제 조건 응답 모델
class DeleteVectorsByConditionResponse(BaseResponse):
    deleted_count: int
    message: str

# Sub/Main 라우터 응답 모델
class IntentRouterResponse(BaseResponse):
    route: Dict
    answer: str
    sources: List[Dict] = []

# LangGraph RAG 응답 모델 (세션 정보 포함)
class LangGraphRAGResponse(BaseResponse):
    response: str
    sources: List[Dict] = []
    category: str = ""
    product_name: str = ""
    session_info: Optional[Dict] = None  # 세션 정보
    initial_intent: str = ""  # 호환성 유지
    initial_topic_summary: str = ""  # 호환성 유지
    conversation_mode: str = "normal"  # 대화 모드
    current_topic: str = ""  # 현재 토픽
    active_product: Optional[str] = ""  # 활성 상품 (Optional로 수정)

# ==============================================
# 상수 및 헬퍼 함수
# ==============================================

# 환경변수에서 데이터 폴더 경로를 가져오거나 기본값 사용
ALLOWED_ROOT = Path(DATA_FOLDER_PATH).expanduser().resolve()

# VectorStore 인스턴스를 반환하는 헬퍼 함수
def _get_vector_store() -> VectorStore:
    """VectorStore 인스턴스를 반환하는 헬퍼 함수"""
    return VectorStore()

# 경로 검증 및 우회 방지 헬퍼 함수
def _validate_and_resolve_target(relative_path_str: str) -> Path:
    """
    상대 경로를 검증하고 절대 경로로 변환합니다.
    
    Returns:
        Path: 검증된 절대 경로
        
    Raises:
        ValueError: 경로 검증 실패 시
        FileNotFoundError: 폴더가 존재하지 않을 때
        NotADirectoryError: 디렉터리가 아닐 때
    """
    rp = relative_path_str.strip()
    p = Path(rp)

    # 절대경로/드라이브/루트 시작 금지
    if p.is_absolute() or p.drive or rp.startswith(("/", "\\")):
        raise ValueError("absolute path is not allowed; provide a path relative to ALLOWED_ROOT")

    # 경로 우회 차단
    if ".." in p.parts:
        raise ValueError("path traversal ('..') is not allowed")

    target = (ALLOWED_ROOT / p).expanduser().resolve(strict=False)

    # ALLOWED_ROOT 하위 경로 확인 (startswith 대신 relative_to 사용)
    try:
        target.relative_to(ALLOWED_ROOT)
    except ValueError:
        raise ValueError("Forbidden path (outside of ALLOWED_ROOT)")

    if not target.exists():
        raise FileNotFoundError(f"folder not found: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"not a directory: {target}")

    return target


# ==============================================
# API 엔드포인트
# ==============================================

# 상태 확인
@router.get("/healthcheck")
async def healthcheck():
    return BaseResponse(status=STATUS_SUCCESS)

# RAG 질의
# @router.post("/query_rag", response_model=QueryRagResponse)
# async def query_rag(input: QueryRagInput):
#     try:
#         orchestrator = Orchestrator()
#         result = orchestrator.query_rag(input.prompt)

#         return QueryRagResponse(
#             status=STATUS_SUCCESS,
#             response=result["response"],
#             sources=result.get("sources", [])  # 여기서 orchestrator가 반환하는 Document.metadata 리스트
#         )
#     except Exception as e:
#         logger.error(f"query_rag failed: {e}")
#         return QueryRagResponse(
#             status=STATUS_FAIL,
#             response=f"질의 처리 중 오류가 발생했습니다: {str(e)}",
#             sources=[]
#         )

# # LLM 전용 답변 생성
# @router.post("/answer_with_llm_only")
# async def answer_with_llm_only(input: LLMOnlyInput):
#     """LLM만 사용하는 간단한 답변 (RAG 없이)"""
#     try:
#         orchestrator = Orchestrator()
#         response = orchestrator.answer_with_llm_only(input.prompt)
#         return LLMOnlyResponse(
#             status=STATUS_SUCCESS,
#             response=response
#         )
#     except Exception as e:
#         logger.error(f"answer_with_llm_only failed: {e}")
#         return LLMOnlyResponse(
#             status=STATUS_FAIL,
#             response=f"LLM 답변 생성 중 오류가 발생했습니다: {str(e)}"
#         )


@router.post("/langgraph/langgraph_rag", response_model=LangGraphRAGResponse)
async def langgraph_rag(input: LangGraphRAGInput):
    """
    LangGraph RAG 엔드포인트 (v2) - 툴콜링 기반
    
    - 툴콜링 기반 워크플로우
    - 중앙 관리자(Supervisor) 패턴
    - 다양한 도구 활용 (chitchat, general_faq, rag_search, product_extraction 등)
    - 가드레일 검사
    - 세션 관리 지원
    """
    logger.info(f"[API] Query: '{input.prompt[:50]}...' | Session: {input.session_id}")
    
    try:
        import time
        import asyncio
        start_time = time.time()
        
        # 타임아웃 설정 (45초로 단축)
        workflow = get_langgraph_workflow()
        
        # Django에서 전달받은 chat_history 활용
        chat_history = getattr(input, 'chat_history', None)
        if chat_history:
            logger.info(f"[API] Using Django chat history: {len(chat_history)} messages")
            # chat_history를 메시지 형태로 변환하여 전달
            result = await asyncio.wait_for(
                asyncio.to_thread(workflow.chat, input.prompt, input.session_id, False, "ko", chat_history),
                timeout=180.0  # 타임아웃 연장 (3분)
            )
        else:
            result = await asyncio.wait_for(
                asyncio.to_thread(workflow.run_workflow, input.prompt, input.session_id),
                timeout=120.0  # 타임아웃 연장 (2분)
            )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 응답 완료 로깅
        session_title = result.get("initial_topic_summary", "") if isinstance(result, dict) else ""
        execution_path = result.get("execution_path", []) if isinstance(result, dict) else []
        path_str = " -> ".join(execution_path) if execution_path else "Unknown"
        logger.info(f"[API] Response time: {response_time:.2f}s | Title: '{session_title}'")
        logger.info(f"[API] Workflow path: {path_str}")
        logger.info("=" * 70)
        
        # 세션 정보에 session_title 추가 (안전한 처리)
        session_info = result.get("session_info", {}) if isinstance(result, dict) else {}
        if isinstance(result, dict) and result.get("initial_topic_summary"):
            session_info["session_title"] = result.get("initial_topic_summary")
        
        # 안전한 응답 데이터 구성
        response_text = result.get("response", "") if isinstance(result, dict) else ""
        sources = result.get("sources", []) if isinstance(result, dict) else []
        category = result.get("category", "") if isinstance(result, dict) else ""
        product_name = result.get("product_name", "") if isinstance(result, dict) else ""
        initial_intent = result.get("initial_intent", "") if isinstance(result, dict) else ""
        initial_topic_summary = result.get("initial_topic_summary", "") if isinstance(result, dict) else ""
        conversation_mode = result.get("conversation_mode", "tool_calling") if isinstance(result, dict) else "tool_calling"
        current_topic = result.get("current_topic", "") if isinstance(result, dict) else ""
        active_product = result.get("active_product", "") if isinstance(result, dict) else ""
        
        response_data = LangGraphRAGResponse(
            status=STATUS_SUCCESS,
            response=response_text,
            sources=sources,
            category=category,
            product_name=product_name,
            session_info=session_info,
            initial_intent=initial_intent,
            initial_topic_summary=initial_topic_summary,
            conversation_mode=conversation_mode,
            current_topic=current_topic,
            active_product=active_product
        )
        
        # UTF-8 인코딩으로 JSON 응답 반환
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=response_data.dict(),
            media_type="application/json; charset=utf-8"
        )
    except asyncio.TimeoutError:
        logger.error(f"[LANGGRAPH RAG] Request timeout (60s)")
        error_response = LangGraphRAGResponse(
            status=STATUS_FAIL,
            response="요청 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
            sources=[],
            category="timeout",
            product_name="",
            session_info={},
            initial_intent="",
            initial_topic_summary="",
            conversation_mode="timeout",
            current_topic="",
            active_product=""
        )
        
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=error_response.dict(),
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"[LANGGRAPH RAG] RAG failed: {e}")
        error_response = LangGraphRAGResponse(
            status=STATUS_FAIL,
            response=f"LangGraph V2 RAG 처리 중 오류가 발생했습니다: {str(e)}",
            sources=[],
            category="error",
            product_name="",
            session_info={},
            initial_intent="",
            initial_topic_summary="",
            conversation_mode="error",
            current_topic="",
            active_product=""
        )
        
        # UTF-8 인코딩으로 JSON 응답 반환
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=error_response.dict(),
            media_type="application/json; charset=utf-8"
        )

# LangGraph 세션 관리 엔드포인트
@router.get("/langgraph/session/{session_id}")
async def get_session_info(session_id: str):
    """세션 정보 조회"""
    try:
        from src.langgraph.session_manager import session_manager
        
        session = session_manager.get_session(session_id)
        if not session:
            return {
                "status": STATUS_FAIL,
                "message": f"세션을 찾을 수 없습니다: {session_id}"
            }
        
        # 대화 히스토리 조회
        conversation_history = session_manager.get_conversation_history(session_id, limit=10)
        message_history = session_manager.get_message_history(session_id, limit=20)
        
        return {
            "status": STATUS_SUCCESS,
            "session_info": session.to_dict(),
            "conversation_history": [turn.to_dict() for turn in conversation_history],
            "message_count": len(message_history),
            "total_turns": len(conversation_history)
        }
    except Exception as e:
        logger.error(f"Session info retrieval failed: {e}")
        return {
            "status": STATUS_FAIL,
            "message": f"세션 정보 조회 중 오류가 발생했습니다: {str(e)}"
        }

# 세션 정리 엔드포인트
@router.delete("/langgraph/session/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        from src.langgraph.session_manager import session_manager
        
        success = session_manager.delete_session(session_id)
        if success:
            return {
                "status": STATUS_SUCCESS,
                "message": f"세션이 삭제되었습니다: {session_id}"
            }
        else:
            return {
                "status": STATUS_FAIL,
                "message": f"세션을 찾을 수 없습니다: {session_id}"
            }
    except Exception as e:
        logger.error(f"Session deletion failed: {e}")
        return {
            "status": STATUS_FAIL,
            "message": f"세션 삭제 중 오류가 발생했습니다: {str(e)}"
        }

# 세션 통계 조회 엔드포인트
@router.get("/langgraph/sessions/stats")
async def get_session_stats():
    """세션 통계 조회"""
    try:
        from src.langgraph.session_manager import session_manager
        
        stats = session_manager.get_session_stats()
        return {
            "status": STATUS_SUCCESS,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Session stats retrieval failed: {e}")
        return {
            "status": STATUS_FAIL,
            "message": f"세션 통계 조회 중 오류가 발생했습니다: {str(e)}"
        }


# LangGraph 워크플로우 상태 조회
@router.get("/langgraph/workflow/status")
async def get_workflow_status():
    """LangGraph V2 워크플로우 상태 조회 (툴콜링 기반)"""
    try:
        workflow = get_langgraph_workflow()
        return {
            "status": STATUS_SUCCESS,
            "workflow_type": "LangGraph RAG Workflow v2 (Tool Calling)",
            "features": [
                "툴콜링 기반 워크플로우",
                "중앙 관리자(Supervisor) 패턴",
                "다양한 도구 활용",
                "가드레일 검사",
                "세션 관리 지원",
                "상품명 추출 및 검색",
                "일반 FAQ 처리"
            ],
            "tools": [
                "chitchat",
                "general_faq", 
                "rag_search",
                "product_extraction",
                "product_search",
                "session_summary",
                "guardrail_check",
                "answer"
            ],
            "nodes": [
                "session_init",
                "supervisor",
                "chitchat",
                "general_faq",
                "product_extraction",
                "product_search",
                "session_summary",
                "rag_search",
                "guardrail_check",
                "answer"
            ]
        }
    except Exception as e:
        logger.error(f"Workflow V2 status check failed: {e}")
        return {
            "status": STATUS_FAIL,
            "message": f"워크플로우 V2 상태 조회 중 오류가 발생했습니다: {str(e)}"
        }

# # Intent 라우팅 기반 처리
# @router.post("/process_with_intent_routing")
# async def process_with_intent_routing(input: IntentRoutingInput):
#     """Intent 분류 후 적절한 처리 방식으로 답변 생성"""
#     try:
#         orchestrator = Orchestrator()
#         result = orchestrator.process_with_intent_routing(input.prompt)
        
#         # result가 딕셔너리인 경우 (새로운 형식)
#         if isinstance(result, dict):
#             return IntentRoutingResponse(
#                 status=STATUS_SUCCESS,
#                 response=result.get("response", ""),
#                 sources=result.get("sources", []),
#                 category=result.get("category", "")
#             )
#         # result가 문자열인 경우 (기존 형식)
#         else:
#             return IntentRoutingResponse(
#                 status=STATUS_SUCCESS,
#                 response=result,
#                 sources=[],
#                 category=""
#             )
#     except Exception as e:
#         logger.error(f"process_with_intent_routing failed: {e}")
#         return IntentRoutingResponse(
#             status=STATUS_FAIL,
#             response=f"Intent 라우팅 처리 중 오류가 발생했습니다: {str(e)}",
#             sources=[],
#             category=""
#         )


# 모든 벡터 삭제
@router.delete("/delete_all_vectors")
async def delete_all_vectors():
    try:
        orchestrator = Orchestrator()
        orchestrator.delete_all_vectors()
        return BaseResponse(status=STATUS_SUCCESS)
    except Exception as e:
        logger.error(f"delete_all_vectors failed: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 삭제 중 오류가 발생했습니다: {str(e)}")

# 조건부 벡터 삭제
@router.delete("/delete_vectors_by_condition")
async def delete_vectors_by_condition(req: DeleteVectorsByConditionReq):
    """특정 조건에 맞는 벡터만 삭제"""
    try:
        orchestrator = Orchestrator()
        deleted_count = orchestrator.delete_vectors_by_condition(req.field, req.value)
        
        return DeleteVectorsByConditionResponse(
            status=STATUS_SUCCESS,
            deleted_count=deleted_count,
            message=f"'{req.field}' = '{req.value}' 조건에 맞는 {deleted_count}개 벡터가 삭제되었습니다."
        )
    except Exception as e:
        logger.error(f"delete_vectors_by_condition failed: {e}")
        raise HTTPException(status_code=500, detail=f"조건부 벡터 삭제 중 오류가 발생했습니다: {str(e)}")

# 개별 파일 업로드
@router.post("/upload_docs_to_rag")
async def upload_docs_to_rag(files: List[UploadFile] = File(...)):
    try:
        orchestrator = Orchestrator()
        all_chunk_ids: List[str] = []
        for file in files:
            chunk_ids = await orchestrator.upload_docs_to_rag(file)
            all_chunk_ids += chunk_ids
        return UploadRagDocsResponse(
            status=STATUS_SUCCESS,
            chunk_ids=all_chunk_ids,
            message=f"{len(files)}개 파일이 성공적으로 업로드되었습니다."
        )
    except Exception as e:
        logger.error(f"upload_docs_to_rag failed: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}")

# 폴더 업로드
@router.post("/ingest_folder")
async def ingest_folder(req: IngestFolderReq):
    """
    JSON Body 예:
    { "root_folder_path": "강령" }
    """
    logger.info(f"Starting folder ingestion for: {req.root_folder_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"ALLOWED_ROOT: {ALLOWED_ROOT}")
    
    try:
        target = _validate_and_resolve_target(req.root_folder_path)
    except ValueError as e:
        logger.error(f"Path validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"Folder not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        logger.error(f"Not a directory: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    orchestrator = Orchestrator()
    try:
        uploaded_ids = await anyio.to_thread.run_sync(
            orchestrator.upload_folder_to_rag,
            str(target),
        )
        logger.info(f"Successfully uploaded {len(uploaded_ids)} chunks")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"ingest failed: {e}")

    return {
        "status": STATUS_SUCCESS,
        "allowed_root": str(ALLOWED_ROOT),
        "resolved_target": str(target),
        "uploaded_chunk_ids_count": len(uploaded_ids),
    }

# 벡터 스토어 초기화

# 상태 확인
@router.get("/vector_store_stats")
async def get_vector_store_stats():
    """벡터 스토어 통계 정보 조회"""
    try:
        store = _get_vector_store()
        stats = store.get_index_stats()
        return {
            "status": STATUS_SUCCESS,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get vector store stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# 카테고리별 RAG 질의
@router.post("/query_rag_by_category")
async def query_rag_by_category(input: QueryRagInput, category: str):
    """카테고리별 RAG 질의"""
    try:
        store = _get_vector_store()
        results = store.similarity_search_by_category(input.prompt, category)
        
        # 결과를 orchestrator 형식으로 변환
        sources = []
        for doc in results:
            meta = dict(doc.metadata or {})
            sources.append(meta)
        
        return QueryRagResponse(
            status=STATUS_SUCCESS, 
            response=f"Found {len(results)} results in category '{category}'",
            sources=sources
        )
    except Exception as e:
        logger.error(f"Category search failed: {e}")
        return QueryRagResponse(
            status=STATUS_FAIL,
            response=f"카테고리별 검색 중 오류가 발생했습니다: {str(e)}",
            sources=[]
        )

# 폴더별 RAG 질의
@router.post("/query_rag_by_folder")
async def query_rag_by_folder(input: QueryRagInput, main_category: str, sub_category: str = None):
    """폴더별 RAG 질의 (강령, 법률, 상품 등)"""
    try:
        store = _get_vector_store()
        results = store.similarity_search_by_folder(input.prompt, main_category, sub_category)
        
        # 결과를 orchestrator 형식으로 변환
        sources = []
        for doc in results:
            meta = dict(doc.metadata or {})
            sources.append(meta)
        
        folder_path = f"{main_category}"
        if sub_category:
            folder_path += f"/{sub_category}"
        
        return QueryRagResponse(
            status=STATUS_SUCCESS,
            response=f"Found {len(results)} results in folder '{folder_path}'",
            sources=sources
        )
    except Exception as e:
        logger.error(f"Folder search failed: {e}")
        return QueryRagResponse(
            status=STATUS_FAIL,
            response=f"폴더별 검색 중 오류가 발생했습니다: {str(e)}",
            sources=[]
        )


# Django 호환 엔드포인트 추가
@router.post("/kb_bank/chatbot/api/chat/", response_model=LangGraphRAGResponse)
async def django_chat_api(input: LangGraphRAGInput):
    """
    Django 호환 채팅 API 엔드포인트
    """
    logger.info(f"[DJANGO API] Query: '{input.prompt[:50]}...' | Session: {input.session_id}")
    
    # 기존 langgraph_rag 함수와 동일한 로직 사용
    return await langgraph_rag(input)