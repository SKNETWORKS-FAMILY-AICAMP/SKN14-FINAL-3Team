from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    """
    인증 미들웨어
    - 미로그인 시: HTML은 302 리다이렉트, API는 401 JSON 응답
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 로그인 페이지와 공개 페이지들 (프로젝트 URL prefix 고려)
        self.public_paths = [
            '/login/',                    # 혹시 direct mount된 경우 대비
            '/kb_bank/login/',           # 실제 프로젝트 로그인 prefix
            '/static/',                  # 정적 파일은 인증 제외
            '/media/',                   # 미디어 파일은 인증 제외
        ]
        
        # API 엔드포인트들
        self.api_paths = [
            '/kb_bank/chatbot/api/',
            '/api/',
        ]
    
    def __call__(self, request):
        # 공개 경로는 인증 체크 건너뛰기
        if self._is_public_path(request.path):
            return self.get_response(request)
        
        # 로그인 상태 확인
        if not request.session.get('user_id'):
            return self._handle_unauthenticated(request)
        
        return self.get_response(request)
    
    def _is_public_path(self, path):
        """공개 경로인지 확인"""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def _is_api_request(self, request):
        """API 요청인지 확인"""
        # Content-Type이 application/json이거나 API 경로인 경우
        content_type = request.content_type
        if content_type and 'application/json' in content_type:
            return True
        
        # API 경로 확인
        for api_path in self.api_paths:
            if request.path.startswith(api_path):
                return True
        
        return False
    
    def _handle_unauthenticated(self, request):
        """미인증 사용자 처리"""
        if self._is_api_request(request):
            # API 요청: 401 JSON 응답
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.',
                'error_code': 'UNAUTHENTICATED'
            }, status=401)
        else:
            # HTML 요청: 302 로그인 페이지 리다이렉트
            login_url = '/kb_bank/login/'
            return HttpResponseRedirect(login_url)
