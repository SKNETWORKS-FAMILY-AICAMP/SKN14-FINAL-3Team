from django.urls import path
from . import views

urlpatterns = [
    path("", views.kb_bank, name="kb_bank"),
]
