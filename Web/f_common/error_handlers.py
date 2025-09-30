from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)

def is_api_request(request):
    """API 요청인지 확인"""
    # Content-Type이 application/json이거나 API 경로인 경우
    content_type = request.content_type
    if content_type and 'application/json' in content_type:
        return True
    
    # API 경로 확인
    api_paths = ['/kb_bank/chatbot/api/', '/api/']
    for api_path in api_paths:
        if request.path.startswith(api_path):
            return True
    
    return False

def handler403(request, exception=None):
    """403 Forbidden 핸들러"""
    logger.warning(f"403 Forbidden: {request.path} - {exception}")
    
    if is_api_request(request):
        return JsonResponse({
            'success': False,
            'message': '접근 권한이 없습니다.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    else:
        return render(request, 'common/error_403.html', status=403)

def handler404(request, exception=None):
    """404 Not Found 핸들러"""
    logger.warning(f"404 Not Found: {request.path} - {exception}")
    
    if is_api_request(request):
        return JsonResponse({
            'success': False,
            'message': '요청한 리소스를 찾을 수 없습니다.',
            'error_code': 'NOT_FOUND'
        }, status=404)
    else:
        return render(request, 'common/error_404.html', status=404)

def handler500(request):
    """500 Internal Server Error 핸들러"""
    # 스택트레이스를 로그에만 기록
    error_traceback = traceback.format_exc()
    logger.error(f"500 Internal Server Error: {request.path}\n{error_traceback}")
    
    if is_api_request(request):
        return JsonResponse({
            'success': False,
            'message': '서버 내부 오류가 발생했습니다.',
            'error_code': 'INTERNAL_SERVER_ERROR'
        }, status=500)
    else:
        return render(request, 'common/error_500.html', status=500)
