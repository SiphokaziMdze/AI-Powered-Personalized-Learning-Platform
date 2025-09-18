# frontend/urls.py
from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    # Main pages
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # API endpoints for authentication
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('logout/', views.user_logout, name='logout'),
]