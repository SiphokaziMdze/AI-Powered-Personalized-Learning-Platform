# backend/frontend/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Q
from learning.models import *
import json

def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    
    context = {
        'title': 'EduCore AI - Intelligent Learning Platform',
        'total_courses': Course.objects.filter(is_published=True).count(),
        'total_lessons': Lesson.objects.filter(course__is_published=True).count(),
        'success_rate': 95,
    }
    return render(request, 'index.html', context)

@login_required
def dashboard(request):
    """Main dashboard view"""
    from learning.views import dashboard as learning_dashboard
    return learning_dashboard(request)

@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    user_courses = Course.objects.filter(
        lessons__userprogress__user=request.user
    ).distinct()
    
    total_lessons = Lesson.objects.filter(course__in=user_courses).count()
    completed_lessons = UserProgress.objects.filter(
        user=request.user,
        is_completed=True
    ).count()
    
    quiz_attempts = QuizAttempt.objects.filter(user=request.user)
    total_quizzes = quiz_attempts.count()
    passed_quizzes = quiz_attempts.filter(is_passed=True).count()
    
    avg_score = quiz_attempts.aggregate(
        avg_score=Avg('score')
    )['avg_score'] or 0
    
    recent_progress = UserProgress.objects.filter(
        user=request.user
    ).select_related('course', 'lesson').order_by('-last_accessed')[:5]
    
    context = {
        'title': 'My Profile - EduCore AI',
        'profile': profile,
        'user_courses': user_courses,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        'total_quizzes': total_quizzes,
        'passed_quizzes': passed_quizzes,
        'quiz_pass_rate': (passed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0,
        'avg_score': round(avg_score, 1),
        'recent_progress': recent_progress,
    }
    
    return render(request, 'profile.html', context)

@login_required
def settings_view(request):
    """User settings view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        try:
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', user.email).strip()
            user.save()
            
            profile.bio = request.POST.get('bio', '').strip()
            profile.location = request.POST.get('location', '').strip()
            profile.timezone = request.POST.get('timezone', 'UTC')
            profile.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
            profile.preferred_learning_style = request.POST.get('preferred_learning_style', '')
            
            birth_date = request.POST.get('birth_date')
            if birth_date:
                try:
                    from datetime import datetime
                    profile.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                except ValueError:
                    profile.birth_date = None
            
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            profile.save()
            
            messages.success(request, 'Settings updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
        
        return redirect('frontend:settings')
    
    context = {
        'title': 'Settings - EduCore AI',
        'profile': profile,
        'timezones': [
            ('UTC', 'UTC'),
            ('US/Eastern', 'Eastern Time (EST/EDT)'),
            ('US/Central', 'Central Time (CST/CDT)'),
            ('US/Mountain', 'Mountain Time (MST/MDT)'),
            ('US/Pacific', 'Pacific Time (PST/PDT)'),
            ('Europe/London', 'London (GMT/BST)'),
            ('Europe/Paris', 'Paris (CET/CEST)'),
            ('Europe/Berlin', 'Berlin (CET/CEST)'),
            ('Asia/Tokyo', 'Tokyo (JST)'),
            ('Asia/Shanghai', 'Shanghai (CST)'),
            ('Australia/Sydney', 'Sydney (AEST/AEDT)'),
        ],
        'learning_styles': [
            ('', 'Not specified'),
            ('visual', 'Visual Learner'),
            ('auditory', 'Auditory Learner'),
            ('kinesthetic', 'Kinesthetic Learner'),
            ('reading', 'Reading/Writing Learner'),
        ]
    }
    
    return render(request, 'settings.html', context)

def login_view(request):
    """Redirect login route to home where modal login exists"""
    return redirect('frontend:home')

def logout_view(request):
    """Logout and redirect"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('frontend:home')

@csrf_exempt
def api_login(request):
    """Handles login via FormData or JSON"""
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    email = request.POST.get("email") or request.POST.get("username")
    password = request.POST.get("password")

    # Fallback to JSON
    if not email and request.body:
        try:
            data = json.loads(request.body)
            email = data.get("email") or data.get("username")
            password = data.get("password")
        except json.JSONDecodeError:
            pass

    if not email or not password:
        return JsonResponse({'success': False, 'message': 'Email and password are required'})

    # Authenticate by email or username
    try:
        u = User.objects.get(email=email)
        user = authenticate(request, username=u.username, password=password)
    except User.DoesNotExist:
        user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'redirect': '/dashboard/',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid credentials'})

    return JsonResponse({'success': False, 'message': 'Invalid credentials'})

@csrf_exempt
def api_signup(request):
    """Handles user registration via FormData or JSON"""
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    first_name = request.POST.get('firstName', '').strip()
    last_name = request.POST.get('lastName', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirmPassword', '')

    # JSON fallback
    if not email and request.body:
        try:
            data = json.loads(request.body)
            first_name = data.get('firstName', '').strip()
            last_name = data.get('lastName', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirmPassword', '')
        except json.JSONDecodeError:
            pass

    if not all([first_name, last_name, email, password]):
        return JsonResponse({'success': False, 'message': 'All fields are required'})
    if password != confirm_password:
        return JsonResponse({'success': False, 'message': 'Passwords do not match'})
    if len(password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'An account with this email already exists'})

    user = User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first_name, last_name=last_name
    )
    from learning.models import UserProfile
    UserProfile.objects.create(user=user)

    login(request, user)
    return JsonResponse({
        'success': True,
        'message': 'Account created successfully',
        'redirect': '/dashboard/',
        'user': {'first_name': first_name, 'last_name': last_name, 'email': email},
    })

