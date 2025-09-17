# backend/learning/views.py

from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from .models import Course, Lesson, Resource, Enrollment, LessonProgress, Quiz

# --- API Signup Endpoint ---
@require_POST
def api_signup(request):
    email = request.POST.get('email', '').strip()
    first = request.POST.get('firstName', '').strip()
    last = request.POST.get('lastName', '').strip()
    password = request.POST.get('password', '')

    if not email or not password or not first or not last:
        return JsonResponse({'ok': False, 'message': 'Missing fields'}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({'ok': False, 'message': 'Email already registered'}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first,
        last_name=last
    )
    login(request, user)
    return JsonResponse({'ok': True, 'user': {'first_name': user.first_name, 'last_name': user.last_name}})


# --- Dashboard View ---
@login_required
def dashboard(request):
    user = request.user

    enrollment = (
        Enrollment.objects
        .filter(user=user)
        .select_related("course")
        .first()
    )
    course = enrollment.course if enrollment else Course.objects.first()

    lessons = Lesson.objects.none()
    completed_count = 0
    total_count = 0

    if course:
        lessons = Lesson.objects.filter(course=course).order_by("id")
        total_count = lessons.count()
        completed_count = LessonProgress.objects.filter(
            user=user, lesson__course=course, completed=True
        ).count()

    overall_progress = round(100 * completed_count / total_count, 1) if total_count else 0

    topics_progress = {
        "process_management": 0,
        "memory_management": 0,
        "file_systems": 0,
        "io_systems": 0,
    }

    recent_resources = Resource.objects.filter(course=course).order_by("-created_at")[:5] if course else []
    upcoming_quizzes = Quiz.objects.filter(course=course, due_at__gte=timezone.now()).order_by("due_at")[:3] if course else []

    context = {
        "title": "Dashboard - OS2 Learn",
        "course": course,
        "lessons": lessons[:10],
        "progress": {
            "overall_progress": overall_progress,
            "chapters_completed": completed_count,
            "videos_watched": 0,
            "quizzes_passed": 0,
            "average_score": 0,
            "study_streak": 0,
            "topics": topics_progress,
        },
        "recent_resources": recent_resources,
        "upcoming_quizzes": upcoming_quizzes,
    }
    return render(request, "dashboard.html", context)
