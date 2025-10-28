#backend/frontend/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Avg, Count, Q
from learning.models import *
import json
import re


def home(request):
    """Landing page - uses modals for login/signup"""
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
    # Import here to avoid circular imports
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
    
    avg_score = quiz_attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
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
            ('US/Eastern', 'Eastern Time'),
            ('US/Pacific', 'Pacific Time'),
            ('Europe/London', 'London'),
            ('Asia/Tokyo', 'Tokyo'),
        ],
        'learning_styles': [
            ('', 'Not specified'),
            ('visual', 'Visual Learner'),
            ('auditory', 'Auditory Learner'),
            ('kinesthetic', 'Kinesthetic Learner'),
        ]
    }
    
    return render(request, 'settings.html', context)

def login_view(request):
    """Login page (form-based)"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or reverse('frontend:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email/username or password.")
    else:
        form = AuthenticationForm(request)

    context = {
        'title': 'Login - EduCore AI',
        'form': form,
    }
    return render(request, 'login.html', context)

def signup_view(request):
    """Signup page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'title': 'Sign Up - EduCore AI',
    }
    return render(request, 'signup.html', context)

def logout_view(request):
    """Logout and redirect"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect(':index')

@csrf_exempt
def api_login(request):
    """API endpoint for login"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({
                'success': False,
                'message': 'Email and password are required'
            })
        
        # Try to authenticate with email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect': '/dashboard/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid email or password'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def api_signup(request):
    """API endpoint for signup"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        first_name = data.get('firstName', '').strip()
        last_name = data.get('lastName', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')
        
        # Validation
        if not all([first_name, last_name, email, password]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            })
        
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match'
            })
        
        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            })
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'An account with this email already exists'
            })
        
        try:
            # Create user
            username = email  # Use email as username
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            UserProfile.objects.create(user=user)
            
            # Log in the user
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully',
                'redirect': '/dashboard/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating account: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})