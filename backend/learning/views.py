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
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .ai_engine import AILearningEngine
from .models import *
from .forms import *
import json
import os

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

@staff_member_required
def content_upload(request):
    """Upload content files (PDFs, videos, images, etc.)"""
    if request.method == 'POST':
        try:
            lesson_id = request.POST.get('lesson_id')
            title = request.POST.get('title', '').strip()
            resource_type = request.POST.get('resource_type', 'note')
            description = request.POST.get('description', '').strip()
            
            if not lesson_id or not title:
                messages.error(request, 'Lesson and title are required')
                return redirect('learning:content_upload')
            
            lesson = get_object_or_404(Lesson, id=lesson_id)
            
            # Handle file upload
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Create resource
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description,
                    file=uploaded_file
                )
                
                messages.success(request, f'File "{uploaded_file.name}" uploaded successfully!')
            
            # Handle URL
            elif 'url' in request.POST and request.POST['url']:
                url = request.POST['url'].strip()
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description,
                    url=url
                )
                messages.success(request, f'URL resource created successfully!')
            
            # Handle text content
            else:
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description
                )
                messages.success(request, f'Text resource created successfully!')
            
            return redirect('learning:content_upload')
            
        except Exception as e:
            messages.error(request, f'Error uploading content: {str(e)}')
            return redirect('learning:content_upload')
    
    # GET request - show upload form
    courses = Course.objects.all().prefetch_related('lessons')
    recent_uploads = Resource.objects.select_related(
        'lesson', 'lesson__course'
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Content Upload',
        'courses': courses,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'learning/admin/content_upload.html', context)

@login_required
def ai_dashboard(request):
    """AI-powered analytics dashboard"""
    ai_engine = AILearningEngine(request.user)
    
    # Get overall performance
    overall_performance = ai_engine.analyze_performance()
    
    # Get course-specific performance
    courses = Course.objects.filter(is_published=True)
    course_analytics = []
    
    for course in courses:
        perf = ai_engine.analyze_performance(course)
        difficulty = ai_engine.get_difficulty_level(course)
        
        course_analytics.append({
            'course': course,
            'performance': perf,
            'difficulty_level': difficulty,
            'predicted_completion': ai_engine.predict_time_to_complete(
                course.lessons.first()
            ) if course.lessons.exists() else 30
        })
    
    # Get learning insights
    insights = ai_engine.get_learning_insights()
    
    # Generate recommendations
    recommendations = ai_engine.generate_recommendations()
    
    context = {
        'title': 'AI Analytics Dashboard',
        'overall_performance': overall_performance,
        'course_analytics': course_analytics,
        'insights': insights,
        'recommendations': recommendations,
        'difficulty_suggestions': {
            'current': ai_engine.get_difficulty_level(),
            'description': 'Your content is automatically adjusted to your performance'
        }
    }
    
    return render(request, 'learning/ai_dashboard.html', context)


@login_required
def adaptive_quiz_view(request, quiz_id):
    """Adaptive quiz that adjusts based on performance"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    ai_engine = AILearningEngine(request.user)
    
    # Get adaptive questions
    adaptive_questions = ai_engine.get_adaptive_quiz_questions(quiz)
    
    if request.method == 'POST':
        # Process quiz submission
        score = 0
        total_points = 0
        
        for question in adaptive_questions:
            total_points += question.points
            selected_choice = request.POST.get(f'question_{question.id}')
            
            if selected_choice:
                choice = Choice.objects.filter(
                    id=selected_choice,
                    is_correct=True
                ).first()
                
                if choice:
                    score += question.points
        
        # Calculate percentage
        percentage = (score / total_points * 100) if total_points > 0 else 0
        
        # Save attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=percentage,
            time_taken=timedelta(minutes=10),  # Track actual time in production
            is_passed=percentage >= quiz.pass_score
        )
        
        # Update progress
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            course=quiz.lesson.course,
            lesson=quiz.lesson
        )
        progress.completion_percentage = min(progress.completion_percentage + 10, 100)
        progress.is_completed = progress.completion_percentage >= 100
        progress.save()
        
        # Generate new recommendations based on performance
        ai_engine.generate_recommendations(quiz.lesson.course)
        
        messages.success(
            request,
            f'Quiz completed! Score: {percentage:.1f}%. '
            f'Difficulty will be adjusted for next quiz.'
        )
        return redirect('learning:lesson_detail', lesson_id=quiz.lesson.id)
    
    context = {
        'title': f'{quiz.title} - Adaptive Quiz',
        'quiz': quiz,
        'questions': adaptive_questions,
        'difficulty_level': ai_engine.get_difficulty_level(quiz.lesson.course),
    }
    
    return render(request, 'learning/adaptive_quiz.html', context)


@staff_member_required
def content_upload(request):
    """Upload content files (PDFs, videos, images, etc.)"""
    if request.method == 'POST':
        try:
            lesson_id = request.POST.get('lesson_id')
            title = request.POST.get('title', '').strip()
            resource_type = request.POST.get('resource_type', 'note')
            description = request.POST.get('description', '').strip()
            
            if not lesson_id or not title:
                messages.error(request, 'Lesson and title are required')
                return redirect('learning:content_upload')
            
            lesson = get_object_or_404(Lesson, id=lesson_id)
            
            # Handle file upload
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Create resource
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description,
                    file=uploaded_file
                )
                
                messages.success(request, f'File "{uploaded_file.name}" uploaded successfully!')
            
            # Handle URL
            elif 'url' in request.POST and request.POST['url']:
                url = request.POST['url'].strip()
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description,
                    url=url
                )
                messages.success(request, f'URL resource created successfully!')
            
            # Handle text content
            else:
                resource = Resource.objects.create(
                    lesson=lesson,
                    title=title,
                    kind=resource_type,
                    content=description
                )
                messages.success(request, f'Text resource created successfully!')
            
            return redirect('learning:content_upload')
            
        except Exception as e:
            messages.error(request, f'Error uploading content: {str(e)}')
            return redirect('learning:content_upload')
    
    # GET request - show upload form
    courses = Course.objects.all().prefetch_related('lessons')
    recent_uploads = Resource.objects.select_related(
        'lesson', 'lesson__course'
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Content Upload',
        'courses': courses,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'learning/admin/content_upload.html', context)


@login_required
@csrf_exempt
def ai_chatbot(request):
    """AI Tutor chatbot for personalized help"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message required'}, status=400)
            
            # AI Engine for context
            ai_engine = AILearningEngine(request.user)
            performance = ai_engine.analyze_performance()
            
            # Simple rule-based responses (replace with actual AI/LLM in production)
            response = generate_ai_response(message, performance)
            
            return JsonResponse({
                'response': response,
                'suggestions': get_ai_suggestions(message)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    context = {
        'title': 'AI Tutor - Get Help'
    }
    return render(request, 'learning/ai_chatbot.html', context)


def generate_ai_response(message, performance):
    """Generate AI tutor response based on message and performance"""
    message_lower = message.lower()
    
    # Context-aware responses
    if 'help' in message_lower or 'stuck' in message_lower:
        if performance['level'] == 'beginner':
            return "I see you're just starting out. Let me break this down into simpler steps. What specific topic are you struggling with?"
        else:
            return "I'm here to help! Based on your progress, you're doing well overall. What specifically can I clarify for you?"
    
    elif 'quiz' in message_lower or 'test' in message_lower:
        return f"Your current quiz performance is {performance['avg_score']:.1f}%. Would you like me to recommend practice materials or explain concepts you found challenging?"
    
    elif 'recommend' in message_lower or 'next' in message_lower:
        if performance['completion_rate'] < 30:
            return "I recommend focusing on completing your current lessons before moving forward. Shall I help you with any specific topic?"
        else:
            return "Based on your progress, you're ready for more advanced topics! Would you like to explore process synchronization or memory management next?"
    
    elif 'os' in message_lower or 'operating' in message_lower:
        return "Operating Systems is a fascinating subject! Are you working on process management, memory systems, or file operations?"
    
    elif 'database' in message_lower or 'sql' in message_lower:
        return "Database concepts can be tricky! Are you learning about SQL queries, normalization, or transaction management?"
    
    else:
        return "I'm your AI tutor! I can help with course recommendations, explain concepts, provide study tips, and answer questions about Operating Systems and Database Systems. What would you like to know?"


def get_ai_suggestions(message):
    """Get suggested follow-up questions"""
    return [
        "What topics should I focus on next?",
        "Explain this concept in simpler terms",
        "Give me practice exercises",
        "How can I improve my quiz scores?"
    ]
