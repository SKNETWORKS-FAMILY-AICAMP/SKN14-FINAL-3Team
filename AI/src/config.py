# import os
# from dotenv import load_dotenv
# import logging

# # 환경변수 로드
# load_dotenv()

# # 로깅 설정
# logger = logging.getLogger(__name__)

# # 필수 환경변수 검증
# def get_required_env(key: str, default: str = None) -> str:
#     """필수 환경변수를 가져오고 없으면 기본값을 사용합니다."""
#     value = os.environ.get(key, default)
#     if not value:
#         logger.warning(f"환경변수 {key}가 설정되지 않았습니다.")
#     return value

# def get_required_int_env(key: str, default: int) -> int:
#     """정수형 환경변수를 가져오고 없으면 기본값을 사용합니다."""
#     try:
#         return int(os.environ.get(key, str(default)))
#     except ValueError:
#         logger.warning(f"환경변수 {key}가 올바른 정수가 아닙니다. 기본값 {default}을 사용합니다.")
#         return default

# # AI 모델 설정
# MODEL_KEY = get_required_env("MODEL_KEY")
# MODEL_NAME = get_required_env("MODEL_NAME", "gpt-3.5-turbo")

# # Pinecone 설정
# PINECONE_KEY = get_required_env("PINECONE_KEY")

# # 임베딩 설정
# EMBEDDING_BACKEND = get_required_env("EMBEDDING_BACKEND")  # openai 또는 huggingface
# EMBEDDING_MODEL_NAME = get_required_env("EMBEDDING_MODEL_NAME") # 예: "text-embedding-3-small" 또는 "bge-m3-small"

# # 벡터 스토어 설정
# VECTOR_STORE_INDEX_NAME = get_required_env("VECTOR_STORE_INDEX_NAME")
# PINECONE_METRIC = get_required_env("PINECONE_METRIC")

# # 문서 처리 설정
# CHUNK_SIZE = get_required_int_env("CHUNK_SIZE", 1000)
# CHUNK_OVERLAP = get_required_int_env("CHUNK_OVERLAP", 200)

# # 데이터 폴더 경로
# DATA_FOLDER_PATH = get_required_env("DATA_FOLDER_PATH", "../SKN14-Final-3Team-Data")

# # 설정 검증
# def validate_config():
#     """설정값들을 검증합니다."""
#     global EMBEDDING_BACKEND
    
#     missing_configs = []
    
#     if not MODEL_KEY:
#         missing_configs.append("MODEL_KEY")
#     if not PINECONE_KEY:
#         missing_configs.append("PINECONE_KEY")
    
#     if missing_configs:
#         logger.error(f"필수 환경변수가 누락되었습니다: {', '.join(missing_configs)}")
#         raise ValueError(f"필수 환경변수가 누락되었습니다: {', '.join(missing_configs)}")
    
#     if EMBEDDING_BACKEND not in ["openai", "huggingface"]:
#         logger.warning(f"알 수 없는 임베딩 백엔드: {EMBEDDING_BACKEND}. 'openai'로 설정합니다.")
#         EMBEDDING_BACKEND = "openai"
    
#     logger.info("설정 검증이 완료되었습니다.")

# # 초기화시 설정 검증
# validate_config()

import os
from dotenv import load_dotenv
import logging

# 환경변수 로드
load_dotenv()

# 로깅 설정
logger = logging.getLogger(__name__)

# 필수 환경변수 검증
def get_required_env(key: str, default: str = None) -> str:
    """필수 환경변수를 가져오고 없으면 기본값을 사용합니다."""
    value = os.environ.get(key, default)
    if not value:
        logger.warning(f"환경변수 {key}가 설정되지 않았습니다.")
    return value

def get_required_int_env(key: str, default: int) -> int:
    """정수형 환경변수를 가져오고 없으면 기본값을 사용합니다."""
    try:
        return int(os.environ.get(key, str(default)))
    except ValueError:
        logger.warning(f"환경변수 {key}가 올바른 정수가 아닙니다. 기본값 {default}을 사용합니다.")
        return default

# AI 모델 설정
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "openai").lower()
MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL")
MODEL_KEY = os.environ.get("MODEL_KEY")
MODEL_NAME = get_required_env("MODEL_NAME", "gpt-3.5-turbo")

# vLLM 장애 시 사용할 OpenAI 폴백 옵션
ENABLE_OPENAI_FALLBACK = os.environ.get("ENABLE_OPENAI_FALLBACK", "true").lower() not in {"0", "false", "no"}
_fallback_name_env = os.environ.get("OPENAI_MODEL_NAME") or os.environ.get("FALLBACK_MODEL_NAME") or "gpt-4o-mini"
FALLBACK_MODEL_NAME = _fallback_name_env if ENABLE_OPENAI_FALLBACK else None

# Pinecone 설정
PINECONE_KEY = get_required_env("PINECONE_KEY")

# 임베딩 설정
EMBEDDING_BACKEND = get_required_env("EMBEDDING_BACKEND")  # openai 또는 huggingface
EMBEDDING_MODEL_NAME = get_required_env("EMBEDDING_MODEL_NAME") # 예: "text-embedding-3-small" 또는 "bge-m3-small"

# 벡터 스토어 설정
VECTOR_STORE_INDEX_NAME = get_required_env("VECTOR_STORE_INDEX_NAME")
PINECONE_METRIC = get_required_env("PINECONE_METRIC")

# 문서 처리 설정
CHUNK_SIZE = get_required_int_env("CHUNK_SIZE", 1000)
CHUNK_OVERLAP = get_required_int_env("CHUNK_OVERLAP", 200)

# 데이터 폴더 경로
DATA_FOLDER_PATH = get_required_env("DATA_FOLDER_PATH", "../SKN14-Final-3Team-Data")

# 설정 검증
def validate_config():
    """설정값들을 검증합니다."""
    # global EMBEDDING_BACKEND
    global EMBEDDING_BACKEND, MODEL_PROVIDER
    
    missing_configs = []
    
    # if not MODEL_KEY:
    if MODEL_PROVIDER not in ["openai", "vllm"]:
        logger.warning(f"알 수 없는 모델 제공자: {MODEL_PROVIDER}. 'openai'로 설정합니다.")
        MODEL_PROVIDER = "openai"

    if (MODEL_PROVIDER == "openai" or EMBEDDING_BACKEND == "openai") and not MODEL_KEY:
        missing_configs.append("MODEL_KEY")
    if not PINECONE_KEY:
        missing_configs.append("PINECONE_KEY")
    
    if missing_configs:
        logger.error(f"필수 환경변수가 누락되었습니다: {', '.join(missing_configs)}")
        raise ValueError(f"필수 환경변수가 누락되었습니다: {', '.join(missing_configs)}")
    
    if MODEL_PROVIDER == "vllm" and not MODEL_BASE_URL:
        logger.warning("MODEL_PROVIDER가 'vllm'으로 설정되었지만 MODEL_BASE_URL이 없습니다. 기본 URL을 사용하려면 환경변수를 설정하세요.")
        raise ValueError("vLLM을 사용하려면 MODEL_BASE_URL 환경변수를 반드시 설정해야 합니다.")

    if ENABLE_OPENAI_FALLBACK and not MODEL_KEY:
        logger.info("OpenAI 폴백이 활성화되어 있지만 MODEL_KEY가 없어 폴백이 비활성화됩니다.")

    if EMBEDDING_BACKEND not in ["openai", "huggingface"]:
        logger.warning(f"알 수 없는 임베딩 백엔드: {EMBEDDING_BACKEND}. 'openai'로 설정합니다.")
        EMBEDDING_BACKEND = "openai"
    
    logger.info("설정 검증이 완료되었습니다.")

# 초기화시 설정 검증
validate_config()
