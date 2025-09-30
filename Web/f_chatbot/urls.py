from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatbot, name="chatbot"),
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/chat/health/", views.health_check, name="chat_health"),
    path("api/chat/histories/", views.get_chat_histories, name="get_chat_histories"),
    path("api/chat/histories/<int:chat_history_id>/messages/", views.get_chat_messages, name="get_chat_messages"),
    path("api/chat/histories/<int:chat_history_id>/delete/", views.delete_chat_history, name="delete_chat_history"),
    path("api/session/<str:session_id>/", views.session_info, name="session_info"),
    path("api/session/<str:session_id>/delete/", views.delete_session, name="delete_session"),
    path("api/sessions/stats/", views.session_stats, name="session_stats"),
    path("pdf/<path:file_path>", views.serve_pdf, name="serve_pdf"),
    path("api/pdf-references/save/", views.save_pdf_references, name="save_pdf_references"),
    path("api/pdf-references/<int:session_msg_id>/", views.get_pdf_references, name="get_pdf_references"),
]
