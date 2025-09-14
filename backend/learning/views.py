# from django.shortcuts import render
# backend/learning/views.py
from django.http import JsonResponse

def ping(request):
    return JsonResponse({"ok": True, "app": "learning"})
