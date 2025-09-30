from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from f_user.models import User
from datetime import datetime
import calendar


@csrf_protect
def login_view(request):
    """로그인 페이지"""
    if request.method == 'POST':
        # 직원 로그인 처리
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        
        # 관리자 로그인 처리
        admin_id = request.POST.get('admin_id')
        admin_password = request.POST.get('admin_password')
        
        # 직원 로그인
        if employee_id and password:
            try:
                # 데이터베이스에는 평문 비밀번호가 저장되어 있음
                user = User.objects.get(employee_id=employee_id, password=password, is_active=True)
                # 세션에 사용자 정보 저장
                request.session['user_id'] = user.seq_id
                request.session['user_name'] = user.name
                request.session['user_email'] = user.email
                request.session['employee_id'] = user.employee_id
                messages.success(request, f'{user.name}님, 환영합니다!')
                return redirect('dashboard')
            except User.DoesNotExist:
                # 직원 로그인 실패
                context = {
                    'login_error': '로그인 정보가 올바르지 않습니다.',
                    'active_tab': 'employee'
                }
                return render(request, 'login/login.html', context)
        
        # 관리자 로그인
        elif admin_id and admin_password:
            # 관리자 로그인 로직 (임시로 간단하게 처리)
            if admin_id == 'admin' and admin_password == 'admin123':
                # 관리자 세션 저장
                request.session['admin_id'] = admin_id
                request.session['is_admin'] = True
                messages.success(request, '관리자님, 환영합니다!')
                return redirect('admin')  # 관리자 페이지로 리다이렉트
            else:
                # 관리자 로그인 실패
                context = {
                    'login_error': '로그인 정보가 올바르지 않습니다.',
                    'active_tab': 'admin'
                }
                return render(request, 'login/login.html', context)
        
        # 입력 필드가 비어있는 경우
        else:
            if employee_id or password:
                # 직원 로그인 필드가 비어있음
                context = {
                    'login_error': '사번과 비밀번호를 모두 입력해주세요.',
                    'active_tab': 'employee'
                }
            elif admin_id or admin_password:
                # 관리자 로그인 필드가 비어있음
                context = {
                    'login_error': '관리자 ID와 비밀번호를 모두 입력해주세요.',
                    'active_tab': 'admin'
                }
            else:
                # 아무것도 입력되지 않음
                context = {
                    'login_error': '로그인 정보를 입력해주세요.',
                    'active_tab': 'employee'
                }
            return render(request, 'login/login.html', context)
    
    # GET 요청 시에는 에러 메시지 없이 렌더링
    return render(request, 'login/login.html', {'login_error': None, 'active_tab': 'employee'})


def dashboard_view(request):
    """대시보드 페이지"""
    try:
        # 세션에서 사용자 ID 가져오기
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "로그인이 필요합니다.")
            return redirect('login')

        try:
            # ID로 사용자 정보 조회
            user = User.objects.get(seq_id=user_id)
        except User.DoesNotExist:
            messages.error(request, "사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.")
            request.session.flush()
            return redirect('login')

        # 캘린더 데이터 생성
        now = datetime.now()
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
        
        # 현재 월이 9월이면 9월을 기본값으로 사용
        if now.month == 9:
            month = 9
        
        # 달력 데이터 생성 (월요일을 주의 시작으로 설정)
        calendar.setfirstweekday(calendar.MONDAY)  # 월요일을 주의 시작으로 설정
        cal = calendar.monthcalendar(year, month)
        
        # 이벤트 데이터 (현재 월에 맞게)
        events = [
            {'date': f'{year}-{month:02d}-15', 'title': '고객 미팅', 'color': '#ffc107'},
            {'date': f'{year}-{month:02d}-20', 'title': '팀 회의', 'color': '#007bff'},
            {'date': f'{year}-{month:02d}-25', 'title': '보고서 제출', 'color': '#28a745'},
        ]
        
        # 현재 월이 9월이면 9월 이벤트로 수정
        if now.month == 9:
            events = [
                {'date': f'{year}-09-15', 'title': '고객 미팅', 'color': '#ffc107'},
                {'date': f'{year}-09-20', 'title': '팀 회의', 'color': '#007bff'},
                {'date': f'{year}-09-25', 'title': '보고서 제출', 'color': '#28a745'},
            ]
        
        context = {
            'user': user,
            # 캘린더 데이터
            'year': year,
            'month': month,
            'calendar': cal,
            'events': events,
            'month_name': calendar.month_name[month],
        }
        
        return render(request, 'dashboard/dashboard.html', context)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard view error: {str(e)}")
        # 에러 발생 시 간단한 에러 페이지 반환
        from django.http import HttpResponse
        return HttpResponse(f"Dashboard 오류가 발생했습니다: {str(e)}", status=500)


def logout_view(request):
    """로그아웃"""
    request.session.flush()
    messages.info(request, '로그아웃되었습니다.')
    return redirect('login:login')
