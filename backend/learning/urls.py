#backend/learning/urls.py
from django.urls import path, include
from . import views
from . import ai_urls

app_name = 'learning'

urlpatterns = [
    # Student/Public views
    path('courses/', views.course_list, name='course_list'),
    path('lesson/<uuid:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('quiz/<uuid:quiz_id>/', views.quiz_view, name='quiz_view'),
    path('quiz/results/<uuid:attempt_id>/', views.quiz_results, name='quiz_results'),
    path('resource/<uuid:resource_id>/', views.resource_view, name='resource_view'),
    path('games/', views.games_list, name='games_list'),

    # AI features
    path('ai/dashboard/', views.ai_dashboard, name='ai_dashboard'),
    path('ai/tutor/', views.ai_chatbot, name='ai_chatbot'),
    path('ai/chat/message/', views.chat_message, name='chat_message'),
    path('ai/chat/conversation/<uuid:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('ai/', include(ai_urls)),

    #games
    path('games/memory-match/', views.memory_match_game, name='memory_match'),
    path('games/process-scheduler/', views.process_scheduler_game, name='process_scheduler'),
    path('games/sql-builder/', views.sql_builder_game, name='sql_builder'),
    path('games/snake/', views.snake_game, name='snake_game'),
    path('games/memory/', views.memory_game, name='memory_game'),
    path('games/quiz/', views.quiz_game, name='quiz_game'),
    path('games/typing/', views.typing_game, name='typing_game'),

    # Admin content management
    path('admin/dashboard/', views.content_dashboard, name='content_dashboard'),
    path('admin/courses/', views.course_management, name='course_management'),
    path('admin/lessons/', views.lesson_management, name='lesson_management'),
    path('admin/lessons/<uuid:course_id>/', views.lesson_management, name='lesson_management_for_course'),
    path('admin/resources/', views.resource_management, name='resource_management'),
    path('admin/resources/<uuid:lesson_id>/', views.resource_management, name='resource_management_for_lesson'),
    path('admin/bulk-upload/', views.bulk_upload_view, name='bulk_upload'),
    path('admin/generate-sample/', views.generate_sample_content, name='generate_sample'),
    path('admin/upload/', views.content_upload, name='content_upload'),
]