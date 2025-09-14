# backend/learning/urls.py
from django.urls import path
from . import views

app_name = "learning" 

urlpatterns = [
    path("ping/", views.ping, name="ping"),
]
