from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    # Student/Public views
    path('courses/', views.course_list, name='course_list'),
    path('lesson/<uuid:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # Admin content management
    path('admin/dashboard/', views.content_dashboard, name='content_dashboard'),
    path('admin/courses/', views.course_management, name='course_management'),
    path('admin/lessons/', views.lesson_management, name='lesson_management'),
    path('admin/lessons/<uuid:course_id>/', views.lesson_management, name='lesson_management_for_course'),
    path('admin/resources/', views.resource_management, name='resource_management'),
    path('admin/resources/<uuid:lesson_id>/', views.resource_management, name='resource_management_for_lesson'),
    path('admin/bulk-upload/', views.bulk_upload_view, name='bulk_upload'),
    path('admin/generate-sample/', views.generate_sample_content, name='generate_sample'),
    path('admin/preview/<uuid:resource_id>/', views.preview_content, name='preview_content'),
    
    # AI Chatbot
    path('ai/tutor/', views.ai_chatbot, name='ai_chatbot'),
    path('ai/chat/message/', views.chat_message, name='chat_message'),
    path('ai/chat/conversation/<uuid:conversation_id>/', views.get_conversation, name='get_conversation'),
]