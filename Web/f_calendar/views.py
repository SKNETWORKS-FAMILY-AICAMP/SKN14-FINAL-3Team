from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import calendar

def calendar_view(request):
    # 현재 날짜
    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # 캘린더 데이터 생성
    cal = calendar.monthcalendar(year, month)
    
    # 이벤트 데이터 (실제로는 DB에서 가져와야 함)
    events = [
        {'date': f'{year}-09-15', 'title': '고객 미팅', 'color': '#ffc107'},
        {'date': f'{year}-09-20', 'title': '팀 회의', 'color': '#007bff'},
        {'date': f'{year}-09-25', 'title': '보고서 제출', 'color': '#28a745'},
    ]
    
    # 디버깅 정보
    print(f"Calendar Debug - Year: {year}, Month: {month}")
    print(f"Calendar data: {cal}")
    
    context = {
        'year': year,
        'month': month,
        'calendar': cal,
        'events': events,
        'month_name': calendar.month_name[month],
    }
    
    return render(request, 'dashboard/calendar.html', context)

def calendar_ajax(request):
    # AJAX 요청 처리
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    cal = calendar.monthcalendar(int(year), int(month))
    
    return JsonResponse({
        'calendar': cal,
        'month_name': calendar.month_name[int(month)]
    })