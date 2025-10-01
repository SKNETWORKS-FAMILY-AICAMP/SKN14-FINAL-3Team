from django.shortcuts import render

def common(request):
    """공통 페이지"""
    return render(request, 'common/common.html')