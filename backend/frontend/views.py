# frontend/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from learning.models import StudentProfile, LessonProgress, Course, Lesson
from django.db.models import Avg, Count, Q
import json

def home_view(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    
    context = {
        'title': 'OS2 Learn - AI-Powered Operating Systems Learning'
    }
    return render(request, 'index.html', context)

@require_POST
def api_signup(request):
    """Handle user registration via AJAX"""
    try:
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        password = request.POST.get('password', '')
        
        # Validation
        if not all([email, first_name, last_name, password]):
            return JsonResponse({
                'success': False, 
                'message': 'All fields are required.'
            }, status=400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False, 
                'message': 'Please enter a valid email address.'
            }, status=400)
        
        # Check password length
        if len(password) < 6:
            return JsonResponse({
                'success': False, 
                'message': 'Password must be at least 6 characters long.'
            }, status=400)
        
        # Check if user exists
        if User.objects.filter(Q(email=email) | Q(username=email)).exists():
            return JsonResponse({
                'success': False, 
                'message': 'An account with this email already exists.'
            }, status=400)
        
        # Create user (use email as username)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Login the user
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Account created successfully!',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred during registration. Please try again.'
        }, status=500)

@require_POST
def api_login(request):
    """Handle user login via AJAX"""
    try:
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        if not email or not password:
            return JsonResponse({
                'success': False, 
                'message': 'Email and password are required.'
            }, status=400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False, 
                'message': 'Please enter a valid email address.'
            }, status=400)
        
        # Try to authenticate with email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!',
                    'user': {
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email
                    }
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Your account has been disabled. Please contact support.'
                }, status=400)
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid email or password.'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred during login. Please try again.'
        }, status=500)

def user_logout(request):
    """Handle user logout"""
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    """Dashboard view for authenticated users"""
    user = request.user
    
    # Get or create student profile
    profile, created = StudentProfile.objects.get_or_create(user=user)
    
    # Calculate progress data from your models
    try:
        # Get user's lesson progress
        completed_lessons = LessonProgress.objects.filter(
            user=user, completed=True
        ).count()
        
        total_lessons = Lesson.objects.count()
        
        # Calculate overall progress
        overall_progress = 0
        if total_lessons > 0:
            overall_progress = int((completed_lessons / total_lessons) * 100)
        
        # Get quiz attempts and scores
        quiz_attempts = user.quiz_attempts.filter(finished_at__isnull=False)
        quizzes_passed = quiz_attempts.filter(score__gte=70).count()
        avg_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Calculate videos watched (you can extend this based on your video tracking)
        videos_watched = LessonProgress.objects.filter(
            user=user, 
            lesson__resources__kind='video'
        ).distinct().count()
        
        # Calculate study streak (simplified - you may want more sophisticated logic)
        study_streak = LessonProgress.objects.filter(user=user).count() // 3  # rough estimate
        
        progress_data = {
            'overall_progress': min(overall_progress, 100),
            'chapters_completed': completed_lessons,
            'videos_watched': videos_watched,
            'quizzes_passed': quizzes_passed,
            'average_score': int(avg_score),
            'study_streak': study_streak,
            'topics': {
                'process_management': min(overall_progress + 15, 100),  # Sample data
                'memory_management': min(overall_progress - 5, 100),
                'file_systems': min(overall_progress - 15, 100),
                'io_systems': min(overall_progress - 25, 100),
            }
        }
        
        # Sample materials data
        materials = [
            {
                'title': 'Process Synchronization Notes',
                'subtitle': 'Semaphores, mutexes, and deadlock prevention',
                'icon': '📄',
                'status_class': 'completed',
                'status_label': 'Completed'
            },
            {
                'title': 'File System Implementation',
                'subtitle': '45 min video • Advanced concepts',
                'icon': '🎥',
                'status_class': 'in-progress',
                'status_label': 'In Progress'
            },
            {
                'title': 'CPU Scheduling Quiz',
                'subtitle': '15 questions • Test your knowledge',
                'icon': '🧩',
                'status_class': 'not-started',
                'status_label': 'Not Started'
            }
        ]
        
        # Sample assessments data
        assessments = [
            {
                'title': 'Midterm Exam: Chapters 1-8',
                'description': 'Comprehensive exam covering process management, memory management, and file systems.',
                'due_in': 'Due in 5 days',
                'urgent': True,
                'action_label': 'Start Practice Test',
                'action_url': '#'
            },
            {
                'title': 'Programming Assignment 3',
                'description': 'Implement a simple file system using C programming language.',
                'due_in': 'Due in 12 days',
                'urgent': False,
                'action_label': 'View Details',
                'action_url': '#'
            }
        ]
        
        # Sample recommendations
        recommendations = [
            {
                'type': 'focus',
                'heading': '📈 Focus Area',
                'text': "You're struggling with deadlock detection. Try the interactive simulation in Chapter 6.",
                'cta_label': 'Start Simulation',
                'cta_url': '#'
            },
            {
                'type': 'next',
                'heading': '🎯 Next Steps',
                'text': 'Great progress on memory management! Ready for virtual memory concepts.',
                'cta_label': 'Continue',
                'cta_url': '#'
            }
        ]
        
    except Exception as e:
        # Fallback to sample data if there's an error
        progress_data = {
            'overall_progress': 42,
            'chapters_completed': 7,
            'videos_watched': 12,
            'quizzes_passed': 5,
            'average_score': 76,
            'study_streak': 3,
            'topics': {
                'process_management': 60,
                'memory_management': 40,
                'file_systems': 25,
                'io_systems': 45,
            }
        }
        materials = []
        assessments = []
        recommendations = []
    
    context = {
        'title': 'Dashboard - OS2 Learn',
        'user': user,
        'progress': progress_data,
        'materials': materials,
        'assessments': assessments,
        'recommendations': recommendations,
        'current_topic': {
            'title': 'Chapter 7: Memory Management',
            'summary': 'Learn about virtual memory, paging, and segmentation techniques in modern operating systems.',
            'status': 'In Progress',
            'read_url': '#',
            'video_url': '#'
        }
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    """User profile view"""
    context = {
        'title': 'Profile - OS2 Learn',
        'user': request.user
    }
    return render(request, 'profile.html', context)

@login_required
def settings_view(request):
    """User settings view"""
    context = {
        'title': 'Settings - OS2 Learn',
        'user': request.user
    }
    return render(request, 'settings.html', context)