# backend/frontend/urls.py
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints (for your existing login/signup in index.html)
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
]