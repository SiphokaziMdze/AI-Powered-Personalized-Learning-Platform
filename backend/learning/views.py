# backend/learning/views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render, redirect

@require_POST
def api_signup(request):
    email = request.POST.get('email', '').strip().lower()
    first = request.POST.get('firstName', '').strip()
    last  = request.POST.get('lastName', '').strip()
    password = request.POST.get('password', '')

    if not all([email, first, last, password]):
        return JsonResponse({"success": False, "message": "Missing fields."}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"success": False, "message": "Email already registered."}, status=400)

    user = User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first, last_name=last
    )
    login(request, user)
    return JsonResponse({
        "success": True,
        "user": {"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
    })

@require_POST
def api_login(request):
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"success": False, "message": "Invalid email or password."}, status=400)
    login(request, user)
    return JsonResponse({
        "success": True,
        "user": {"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
    })

@login_required
def dashboard(request):
    # temporary dummy progress
    progress = {
        "overall_progress": 42,
        "chapters_completed": 7,
        "videos_watched": 12,
        "quizzes_passed": 5,
        "average_score": 76,
        "study_streak": 3,
        "topics": {
            "process_management": 60,
            "memory_management": 40,
            "file_systems": 25,
            "io_systems": 45,
        },
    }
    return render(request, "dashboard.html", {"title": "My Dashboard", "progress": progress})

def user_logout(request):
    logout(request)
    return redirect("home")
