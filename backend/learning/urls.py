# backend/learning/urls.py
from django.urls import path
from . import views

app_name = "learning" 

urlpatterns = [
    path('ping/', views.ping, name='learning_ping'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('api/login/', views.api_login, name='api_login'),
    path('logout/', views.user_logout, name='logout'),
]
