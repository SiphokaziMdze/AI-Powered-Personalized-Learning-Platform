# backend/learning/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import *
from .forms import *
import json

# ============ PUBLIC/STUDENT VIEWS ============

@login_required
def dashboard(request):
    """Main dashboard view"""
    user_courses = Course.objects.filter(
        lessons__userprogress__user=request.user
    ).distinct()
    
    total_lessons = Lesson.objects.filter(course__in=user_courses).count()
    completed_lessons = UserProgress.objects.filter(
        user=request.user,
        is_completed=True
    ).count()
    
    overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    recent_progress = UserProgress.objects.filter(
        user=request.user
    ).select_related('course', 'lesson').order_by('-last_accessed')[:5]
    
    recommendations = AIRecommendation.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-priority', '-created_at')[:3]
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'user_courses': user_courses,
        'overall_progress': round(overall_progress, 1),
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'recent_progress': recent_progress,
        'recommendations': recommendations,
        'study_streak': profile.study_streak,
        'os2_progress': 78,
        'db3_progress': 65,
        'progress': {
            'overall_progress': round(overall_progress, 1),
            'study_streak': profile.study_streak,
        }
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def course_list(request):
    """List all published courses"""
    courses = Course.objects.filter(is_published=True).prefetch_related('lessons')
    
    context = {
        'courses': courses,
        'title': 'Courses - EduCore AI'
    }
    return render(request, 'learning/course_list.html', context)

@login_required
def lesson_detail(request, lesson_id):
    """Display lesson detail"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Track progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=lesson.course,
        lesson=lesson,
        defaults={'completion_percentage': 0}
    )
    
    progress.last_accessed = timezone.now()
    progress.save()
    
    resources = lesson.resources.all()
    quizzes = lesson.quizzes.filter(is_active=True)
    
    context = {
        'lesson': lesson,
        'resources': resources,
        'quizzes': quizzes,
        'progress': progress,
        'title': f'{lesson.title} - EduCore AI'
    }
    
    return render(request, 'learning/lesson_detail.html', context)

# ============ ADMIN VIEWS ============

@staff_member_required
def content_dashboard(request):
    """Main content management dashboard"""
    context = {
        'title': 'Content Management - EduCore AI',
        'courses': Course.objects.annotate(
            lesson_count=Count('lessons'),
            resource_count=Count('lessons__resources')
        ).order_by('-created_at'),
        'total_lessons': Lesson.objects.count(),
        'total_resources': Resource.objects.count(),
        'total_quizzes': Quiz.objects.count(),
    }
    return render(request, 'learning/admin/content_dashboard.html', context)

@staff_member_required
def course_management(request):
    """Manage courses"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('learning:lesson_management_for_course', course_id=course.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CourseForm()
    
    courses = Course.objects.annotate(
        lesson_count=Count('lessons')
    ).order_by('-created_at')
    
    context = {
        'title': 'Course Management',
        'form': form,
        'courses': courses,
    }
    return render(request, 'learning/admin/course_management.html', context)

@staff_member_required
def lesson_management(request, course_id=None):
    """Manage lessons"""
    course = get_object_or_404(Course, id=course_id) if course_id else None
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f'Lesson "{lesson.title}" created successfully!')
            return redirect('learning:lesson_management_for_course', course_id=lesson.course.id)
    else:
        form = LessonForm(initial={'course': course} if course else {})
    
    lessons = Lesson.objects.select_related('course')
    if course:
        lessons = lessons.filter(course=course)
    
    context = {
        'title': 'Lesson Management',
        'form': form,
        'lessons': lessons.order_by('course', 'order'),
        'course': course,
    }
    return render(request, 'learning/admin/lesson_management.html', context)

@staff_member_required
def resource_management(request, lesson_id=None):
    """Manage resources"""
    lesson = get_object_or_404(Lesson, id=lesson_id) if lesson_id else None
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save()
            messages.success(request, f'Resource "{resource.title}" created successfully!')
            return redirect('learning:resource_management_for_lesson', lesson_id=resource.lesson.id)
    else:
        form = ResourceForm(initial={'lesson': lesson} if lesson else {})
    
    resources = Resource.objects.select_related('lesson', 'lesson__course')
    if lesson:
        resources = resources.filter(lesson=lesson)
    
    context = {
        'title': 'Resource Management',
        'form': form,
        'resources': resources.order_by('lesson'),
        'lesson': lesson,
    }
    return render(request, 'learning/admin/resource_management.html', context)

@staff_member_required
def bulk_upload_view(request):
    """Bulk upload content"""
    if request.method == 'POST' and 'json_file' in request.FILES:
        try:
            json_file = request.FILES['json_file']
            data = json.loads(json_file.read().decode('utf-8'))
            
            created_courses = 0
            created_lessons = 0
            created_resources = 0
            
            for course_data in data.get('courses', []):
                course, created = Course.objects.get_or_create(
                    slug=course_data['slug'],
                    defaults={
                        'title': course_data['title'],
                        'description': course_data.get('description', ''),
                        'is_published': course_data.get('is_published', True)
                    }
                )
                if created:
                    created_courses += 1
                
                for lesson_data in course_data.get('lessons', []):
                    lesson, created = Lesson.objects.get_or_create(
                        course=course,
                        order=lesson_data['order'],
                        defaults={
                            'title': lesson_data['title'],
                            'content': lesson_data.get('content', ''),
                        }
                    )
                    if created:
                        created_lessons += 1
                    
                    for resource_data in lesson_data.get('resources', []):
                        resource, created = Resource.objects.get_or_create(
                            lesson=lesson,
                            title=resource_data['title'],
                            defaults={
                                'kind': resource_data.get('kind', 'note'),
                                'content': resource_data.get('content', ''),
                            }
                        )
                        if created:
                            created_resources += 1
            
            messages.success(
                request, 
                f'Upload successful! Created {created_courses} courses, '
                f'{created_lessons} lessons, {created_resources} resources.'
            )
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('learning:bulk_upload')
    
    return render(request, 'learning/admin/bulk_upload.html', {
        'title': 'Bulk Upload'
    })

@staff_member_required
def generate_sample_content(request):
    """Generate sample content"""
    if request.method == 'POST':
        try:
            os_course, created = Course.objects.get_or_create(
                slug='operating-systems-2',
                defaults={
                    'title': 'Operating Systems 2',
                    'description': 'Advanced OS concepts',
                    'is_published': True
                }
            )
            
            if created:
                for i, title in enumerate(['Process Management', 'Memory Systems', 'File Systems'], 1):
                    lesson = Lesson.objects.create(
                        course=os_course,
                        title=title,
                        order=i,
                        content=f'Content for {title}'
                    )
                    
                    Resource.objects.create(
                        lesson=lesson,
                        title=f'{title} - Notes',
                        kind='note',
                        content=f'Study notes for {title}'
                    )
                
                messages.success(request, 'Sample content created successfully!')
            else:
                messages.info(request, 'Sample content already exists.')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'learning/admin/generate_sample.html', {
        'title': 'Generate Sample Content'
    })

@staff_member_required
def preview_content(request, resource_id):
    """Preview content"""
    resource = get_object_or_404(Resource, id=resource_id)
    return render(request, 'learning/admin/content_preview.html', {
        'resource': resource
    })

# Placeholder for AI chatbot views
@login_required
def ai_chatbot(request):
    """AI Chatbot - Coming soon"""
    return render(request, 'learning/ai_chatbot_placeholder.html', {
        'title': 'AI Tutor - Coming Soon'
    })

@login_required
def chat_message(request):
    """Chat message API - Coming soon"""
    return JsonResponse({'error': 'AI Chatbot coming soon'}, status=501)

@login_required
def get_conversation(request, conversation_id):
    """Get conversation - Coming soon"""
    return JsonResponse({'error': 'AI Chatbot coming soon'}, status=501)

# Add this placeholder view for ai_dashboard
@login_required
def ai_dashboard(request):
    """AI Dashboard - Coming soon"""
    return render(request, 'learning/ai_dashboard_placeholder.html', {
        'title': 'AI Dashboard - Coming Soon'
    })