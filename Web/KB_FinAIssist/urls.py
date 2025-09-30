from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import render
from f_login.views import dashboard_view, logout_view

def admin_view(request):
    return render(request, 'admin/admin.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/kb_bank/login/"), name="main"),
    path("kb_bank/", include([
        path("login/", include("f_login.urls", namespace="login")),
        path("logout/", logout_view, name="logout"),
        path("dashboard/", dashboard_view, name="dashboard"),
        path("chatbot/", include("f_chatbot.urls")),
        path("credit_assessment/", include("f_loan.urls", namespace="credit_assessment")),
        path("admin/", admin_view, name="admin"),
    ])),
]