# backend/learning/ai_urls.py
"""
URL patterns for AI-powered features
"""
from django.urls import path
from . import ai_views

app_name = 'ai'

urlpatterns = [
    # AI Dashboard and Analytics
    path('dashboard/', ai_views.ai_dashboard, name='dashboard'),
    path('analytics/', ai_views.get_learning_analytics, name='analytics'),
    
    # AI Chatbot/Tutor
    path('chatbot/', ai_views.ai_chatbot, name='chatbot'),
    path('chat/message/', ai_views.handle_chat_message, name='chat_message'),
    path('chat/conversation/<uuid:conversation_id>/', ai_views.get_conversation, name='get_conversation'),
    
    # Personalized Recommendations
    path('recommendations/', ai_views.get_recommendations, name='recommendations'),
    path('recommendations/<uuid:recommendation_id>/acted/', ai_views.mark_recommendation_acted, name='mark_acted'),
    
    # Adaptive Content
    path('adaptive-content/', ai_views.get_adaptive_content, name='adaptive_content'),
    
    # AI Learning Tools
    path('lesson/<uuid:lesson_id>/explanation/', ai_views.generate_lesson_explanation, name='lesson_explanation'),
    path('lesson/<uuid:lesson_id>/generate-quiz/', ai_views.generate_quiz_from_content, name='generate_quiz'),
]