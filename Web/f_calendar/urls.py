from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("ajax/", views.calendar_ajax, name="calendar_ajax"),
]
