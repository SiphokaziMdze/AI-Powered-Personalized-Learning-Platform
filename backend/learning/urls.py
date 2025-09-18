# backend/learning/urls.py
from django.urls import path
from . import views

app_name = "learning" 

urlpatterns = [
    # Learning-specific views
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('flashcards/', views.flashcards, name='flashcards'),
    path('ask_ai/', views.ask_ai, name='ask_ai'),
]
