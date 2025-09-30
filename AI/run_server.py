#!/usr/bin/env python3
"""
KB금융 RAG API 서버 실행 스크립트

사용법:
    python run_server.py [--host HOST] [--port PORT] [--reload]

예시:
    python run_server.py --host 0.0.0.0 --port 8000 --reload
"""
import argparse
import uvicorn
import logging

def main():
    parser = argparse.ArgumentParser(description="KB금융 RAG API 서버 실행")
    parser.add_argument("--host", default="127.0.0.1", help="서버 호스트 (기본값: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="서버 포트 (기본값: 8000)")
    parser.add_argument("--reload", action="store_true", help="개발 모드 - 파일 변경시 자동 재시작 (권장하지 않음)")
    parser.add_argument("--workers", type=int, default=1, help="워커 프로세스 수 (기본값: 1)")
    parser.add_argument("--no-reload", action="store_true", help="자동 재시작 비활성화 (권장)")
    
    args = parser.parse_args()
    
    # 로깅 설정 (main.py에서 이미 설정됨)
    logger = logging.getLogger(__name__)
    
    # 리로드 설정 결정
    enable_reload = args.reload and not args.no_reload
    
    logger.info(f"KB금융 RAG API 서버를 시작합니다...")
    logger.info(f"호스트: {args.host}")
    logger.info(f"포트: {args.port}")
    logger.info(f"리로드 모드: {enable_reload}")
    logger.info(f"워커 수: {args.workers if not enable_reload else 1}")
    
    if enable_reload:
        logger.warning("⚠️  리로드 모드가 활성화되어 있습니다. 성능이 저하될 수 있습니다.")
        logger.warning("💡 권장: --no-reload 옵션을 사용하여 안정적인 실행을 권장합니다.")
    
    try:
        uvicorn.run(
            "src.main:app",
            host=args.host,
            port=args.port,
            reload=enable_reload,
            workers=args.workers if not enable_reload else 1,
            access_log=True,
            log_level="info",
            timeout_keep_alive=30,  # Keep-alive 타임아웃
            timeout_graceful_shutdown=30,  # Graceful shutdown 타임아웃
            limit_concurrency=1000,  # 동시 연결 제한
            limit_max_requests=1000  # 최대 요청 수 제한
        )
    except KeyboardInterrupt:
        logger.info("서버가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"서버 실행 중 오류가 발생했습니다: {e}", exc_info=True)

if __name__ == "__main__":
    main()
