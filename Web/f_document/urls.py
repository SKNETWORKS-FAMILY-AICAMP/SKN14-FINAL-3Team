from django.urls import path
from . import views

urlpatterns = [
    path("", views.document, name="document"),
    path('upload/', views.document_upload_page, name='document_upload_page'),
    path('api/upload/', views.upload_api, name='upload_api'),
]