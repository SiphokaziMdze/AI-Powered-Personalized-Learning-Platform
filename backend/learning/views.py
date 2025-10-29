# backend/learning/views.py 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, datetime
from .ai_engine import AILearningEngine
from .models import *
from .forms import *
import json
from .ai_services import (
    HuggingFaceAIService,
    PersonalizedLearningEngine,
    AITutorService
)

# ============ STUDENT VIEWS ============

@login_required
def dashboard(request):
    """Enhanced dashboard with quizzes, resources, and games"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get or create sample courses if they don't exist
    try:
        os2_course = Course.objects.get(slug='operating-systems-2')
    except Course.DoesNotExist:
        # Create sample course if it doesn't exist
        os2_course = Course.objects.create(
            title='Operating Systems 2',
            slug='operating-systems-2',
            description='Advanced OS concepts',
            is_published=True
        )
    
    try:
        db3_course = Course.objects.get(slug='database-systems-3')
    except Course.DoesNotExist:
        # Create sample course if it doesn't exist
        db3_course = Course.objects.create(
            title='Database Systems 3',
            slug='database-systems-3',
            description='Advanced database concepts',
            is_published=True
        )
    
    # Overall progress calculation
    user_courses = Course.objects.filter(is_published=True)
    total_lessons = Lesson.objects.filter(course__in=user_courses).count()
    completed_lessons = UserProgress.objects.filter(
        user=user,
        is_completed=True
    ).count()
    overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # OS2 Data
    os2_data = get_course_data(user, os2_course) if os2_course else {}
    
    # DB3 Data
    db3_data = get_course_data(user, db3_course) if db3_course else {}
    
    # AI Recommendations - FIX: Only generate if courses exist
    recommendations = []
    try:
        if os2_course or db3_course:
            ai_engine = AILearningEngine(user)
            recommendations = ai_engine.generate_recommendations()[:5]
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        recommendations = []
    
    # Recent activity
    recent_progress = UserProgress.objects.filter(
        user=user
    ).select_related('course', 'lesson').order_by('-last_accessed')[:5]
    
    context = {
        'title': 'Dashboard - EduCore AI',
        'overall_progress': round(overall_progress, 1),
        'study_streak': profile.study_streak,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'recommendations': recommendations,
        'recent_progress': recent_progress,
        
        # OS2 specific
        'os2_progress': os2_data.get('progress', 0),
        'os2_quizzes': os2_data.get('quizzes', []),
        'os2_resources': os2_data.get('resources', []),
        'os2_current_lesson': os2_data.get('current_lesson'),
        'os2_topics': os2_data.get('topics', []),
        
        # DB3 specific
        'db3_progress': db3_data.get('progress', 0),
        'db3_quizzes': db3_data.get('quizzes', []),
        'db3_resources': db3_data.get('resources', []),
        'db3_current_lesson': db3_data.get('current_lesson'),
        'db3_topics': db3_data.get('topics', []),
    }
    
    return render(request, 'dashboard.html', context)


def get_course_data(user, course):
    """Get comprehensive course data including quizzes and resources"""
    if not course:
        return {}
    
    # Progress
    course_progress = UserProgress.objects.filter(
        user=user,
        course=course
    )
    total_lessons = course.lessons.count()
    completed = course_progress.filter(is_completed=True).count()
    progress = (completed / total_lessons * 100) if total_lessons > 0 else 0
    
    # Current lesson (first incomplete or most recent)
    current_progress = course_progress.filter(is_completed=False).order_by('lesson__order').first()
    if not current_progress and total_lessons > 0:
        current_progress = course_progress.order_by('-last_accessed').first()
    
    current_lesson = current_progress.lesson if current_progress else (course.lessons.first() if total_lessons > 0 else None)
    
    # Quizzes with user attempt data
    quizzes = []
    for lesson in course.lessons.filter(is_published=True):
        for quiz in lesson.quizzes.filter(is_active=True):
            # Get user's best attempt
            best_attempt = QuizAttempt.objects.filter(
                user=user,
                quiz=quiz
            ).order_by('-score').first()
            
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'pass_score': quiz.pass_score,
                'question_count': quiz.questions.count(),
                'user_attempted': best_attempt is not None,
                'user_best_score': best_attempt.score if best_attempt else None,
            }
            quizzes.append(quiz_data)
    
    # Resources
    resources = Resource.objects.filter(
        lesson__course=course,
        lesson__is_published=True
    ).select_related('lesson').order_by('-created_at')[:12]
    
    # Topic progress breakdown
    topics = []
    for lesson in course.lessons.filter(is_published=True)[:5]:
        lesson_progress = UserProgress.objects.filter(
            user=user,
            lesson=lesson
        ).first()
        
        topics.append({
            'name': lesson.title,
            'progress': int(lesson_progress.completion_percentage) if lesson_progress else 0
        })
    
    return {
        'progress': round(progress, 1),
        'quizzes': quizzes,
        'resources': resources,
        'current_lesson': current_lesson,
        'topics': topics,
    }


@login_required
def course_list(request):
    """List all published courses"""
    courses = Course.objects.filter(is_published=True).prefetch_related('lessons')
    
    # Add progress data for each course
    course_data = []
    for course in courses:
        total = course.lessons.count()
        completed = UserProgress.objects.filter(
            user=request.user,
            course=course,
            is_completed=True
        ).count()
        
        course_data.append({
            'course': course,
            'total_lessons': total,
            'completed_lessons': completed,
            'progress': (completed / total * 100) if total > 0 else 0
        })
    
    context = {
        'course_data': course_data,
        'title': 'Courses - EduCore AI'
    }
    return render(request, 'learning/course_list.html', context)


@login_required
def lesson_detail(request, lesson_id):
    """Display lesson detail with resources and quizzes"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Track progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=lesson.course,
        lesson=lesson,
        defaults={'completion_percentage': 0}
    )
    
    # Update last accessed
    progress.last_accessed = timezone.now()
    if progress.completion_percentage < 100:
        progress.completion_percentage = min(progress.completion_percentage + 5, 100)
    progress.is_completed = progress.completion_percentage >= 100
    progress.save()
    
    # Get resources and quizzes
    resources = lesson.resources.all()
    quizzes = lesson.quizzes.filter(is_active=True)
    
    # Add user attempt data to quizzes
    quiz_data = []
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
        best_attempt = attempts.order_by('-score').first()
        
        quiz_data.append({
            'quiz': quiz,
            'attempts_count': attempts.count(),
            'best_score': best_attempt.score if best_attempt else None,
            'is_passed': best_attempt.is_passed if best_attempt else False,
        })
    
    # Get next and previous lessons
    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        order__gt=lesson.order
    ).order_by('order').first()
    
    prev_lesson = Lesson.objects.filter(
        course=lesson.course,
        order__lt=lesson.order
    ).order_by('-order').first()
    
    context = {
        'lesson': lesson,
        'resources': resources,
        'quiz_data': quiz_data,
        'progress': progress,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'title': f'{lesson.title} - EduCore AI'
    }
    
    return render(request, 'learning/lesson_detail.html', context)


@login_required
def quiz_view(request, quiz_id):
    """Take a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    if request.method == 'POST':
        # Process quiz submission
        return process_quiz_submission(request, quiz)
    
    # GET - show quiz
    questions = quiz.questions.all().prefetch_related('choices')
    
    # Get previous attempts
    attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz
    ).order_by('-started_at')
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempts': attempts,
        'title': f'{quiz.title} - Quiz'
    }
    
    return render(request, 'learning/quiz.html', context)


def process_quiz_submission(request, quiz):
    """Process quiz answers and calculate score"""
    questions = quiz.questions.all()
    
    total_points = sum(q.points for q in questions)
    earned_points = 0
    
    answers = {}
    
    for question in questions:
        selected_choice_id = request.POST.get(f'question_{question.id}')
        
        if selected_choice_id:
            try:
                selected_choice = Choice.objects.get(id=selected_choice_id)
                answers[str(question.id)] = {
                    'selected': selected_choice_id,
                    'correct': selected_choice.is_correct
                }
                
                if selected_choice.is_correct:
                    earned_points += question.points
            except Choice.DoesNotExist:
                pass
    
    # Calculate percentage
    score = (earned_points / total_points * 100) if total_points > 0 else 0
    is_passed = score >= quiz.pass_score
    
    # Save attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        time_taken=timedelta(minutes=10),  # TODO: Track actual time
        completed_at=timezone.now(),
        is_passed=is_passed
    )
    
    # Update lesson progress
    progress, _ = UserProgress.objects.get_or_create(
        user=request.user,
        course=quiz.lesson.course,
        lesson=quiz.lesson
    )
    
    if is_passed:
        progress.completion_percentage = min(progress.completion_percentage + 20, 100)
        progress.is_completed = progress.completion_percentage >= 100
        progress.save()
    
    # Show results
    messages.success(
        request,
        f'Quiz completed! Score: {score:.1f}% - {"Passed" if is_passed else "Failed"}'
    )
    
    return redirect('learning:quiz_results', attempt_id=attempt.id)


@login_required
def quiz_results(request, attempt_id):
    """Show quiz results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Get all questions with user's answers
    questions = attempt.quiz.questions.all().prefetch_related('choices')
    
    context = {
        'attempt': attempt,
        'questions': questions,
        'title': f'Results - {attempt.quiz.title}'
    }
    
    return render(request, 'learning/quiz_results.html', context)


@login_required
def resource_view(request, resource_id):
    """View a specific resource"""
    resource = get_object_or_404(Resource, id=resource_id)
    
    # Track that user accessed this resource
    progress, _ = UserProgress.objects.get_or_create(
        user=request.user,
        course=resource.lesson.course,
        lesson=resource.lesson
    )
    progress.last_accessed = timezone.now()
    progress.save()
    
    context = {
        'resource': resource,
        'title': f'{resource.title} - {resource.lesson.title}'
    }
    
    return render(request, 'learning/resource_view.html', context)


@login_required
def games_list(request):
    """List all learning games"""
    context = {
        'title': 'Learning Games - EduCore AI',
        'games': [
            {
                'title': 'Memory Match',
                'description': 'Match computer science terms with their definitions',
                'icon': '🧠',
                'url': '/learning/games/memory-match/',
                'coming_soon': False,
            },
            {
                'title': 'Process Scheduler',
                'description': 'Simulate different CPU scheduling algorithms',
                'icon': '⚙️',
                'url': '/learning/games/process-scheduler/',
                'coming_soon': False,
            },
            {
                'title': 'SQL Query Builder',
                'description': 'Build SQL queries to solve database challenges',
                'icon': '💾',
                'url': '/learning/games/sql-builder/',
                'coming_soon': False,
            },
            {
                'title': 'Database Normalizer',
                'description': 'Normalize tables to proper database forms',
                'icon': '📊',
                'url': '/learning/games/database-normalizer/',
                'coming_soon': False,
            },
            {
                'title': 'Code Snake',
                'description': 'Classic snake game with a coding twist',
                'icon': '🐍',
                'url': '/learning/games/snake/',
                'coming_soon': False,
            },
            {
                'title': 'Memory Match',
                'description': 'Match programming concepts and symbols',
                'icon': '🧠',
                'url': '/learning/games/memory/',
                'coming_soon': False,
            },
            {
                'title': 'Quick Quiz',
                'description': 'Test your knowledge with rapid-fire questions',
                'icon': '❓',
                'url': '/learning/games/quiz/',
                'coming_soon': False,
            },
            {
                'title': 'Code Typer',
                'description': 'Improve your typing speed with code snippets',
                'icon': '⌨️',
                'url': '/learning/games/typing/',
                'coming_soon': False,
            },
        ]
    }
    return render(request, 'learning/games_list.html', context)


@login_required
def snake_game(request):
    """Code Snake game"""
    context = {
        'title': 'Code Snake - Learning Game'
    }
    return render(request, 'learning/games/snake_game.html', context)


@login_required
def memory_game(request):
    """Memory Match game"""
    context = {
        'title': 'Memory Match - Learning Game'
    }
    return render(request, 'learning/games/memory_game.html', context)


@login_required
def quiz_game(request):
    """Quick Quiz game"""
    context = {
        'title': 'Quick Quiz - Learning Game'
    }
    return render(request, 'learning/games/quiz_game.html', context)


@login_required
def typing_game(request):
    """Code Typer game"""
    context = {
        'title': 'Code Typer - Learning Game'
    }
    return render(request, 'learning/games/typing_game.html', context)
    
    return render(request, 'learning/games_list.html', context)


@login_required
def memory_match_game(request):
    """Memory match game"""
    context = {
        'title': 'Memory Match - Learning Game'
    }
    return render(request, 'learning/games/memory_match.html', context)


@login_required
def process_scheduler_game(request):
    """Process scheduler simulator game"""
    context = {
        'title': 'Process Scheduler - Learning Game'
    }
    return render(request, 'learning/games/process_scheduler.html', context)


@login_required
def sql_builder_game(request):
    """SQL query builder challenge game"""
    context = {
        'title': 'SQL Query Builder - Learning Game'
    }
    return render(request, 'learning/games/sql_builder.html', context)


# ============ AI VIEWS ============

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
    }
    
    return render(request, 'learning/ai_dashboard.html', context)

@login_required
def ai_chatbot(request):
    """AI Tutor chatbot page"""
    # Get or create a conversation for today
    conversation, created = ChatConversation.objects.get_or_create(
        user=request.user,
        created_at__date=datetime.now().date(),
        defaults={'title': f"Chat {datetime.now().strftime('%b %d, %Y')}"}
    )
    
    # Get recent conversations
    recent_conversations = ChatConversation.objects.filter(
        user=request.user
    )[:10]
    
    context = {
        'title': 'AI Tutor - Get Help',
        'conversation': conversation,
        'recent_conversations': recent_conversations,
    }
    return render(request, 'learning/ai_chatbot.html', context)

@login_required
@csrf_exempt
def chat_message(request):
    """Handle chat messages with AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not message:
                return JsonResponse({'error': 'Message required'}, status=400)
            
            # Get or create conversation
            if conversation_id:
                conversation = ChatConversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )
            else:
                conversation = ChatConversation.objects.create(
                    user=request.user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            # Save user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # Get chat history
            chat_history = [
                {'role': msg.role, 'content': msg.content}
                for msg in conversation.messages.all()[:20]  # Last 20 messages
            ]
            
            # Get AI response
            ai_service = GeminiAIService()
            result = ai_service.chat_with_ai(request.user, message, chat_history[:-1])
            
            if result['success']:
                # Save AI response
                ai_message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=result['response']
                )
                
                return JsonResponse({
                    'success': True,
                    'response': result['response'],
                    'suggestions': result.get('suggestions', []),
                    'conversation_id': str(conversation.id)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'response': result['response']
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error. Please try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_conversation(request, conversation_id):
    """Get conversation history"""
    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        
        messages = [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in conversation.messages.all()
        ]
        
        return JsonResponse({
            'success': True,
            'conversation_id': str(conversation.id),
            'title': conversation.title,
            'messages': messages
        })
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)


def generate_ai_response(message, performance):
    """Generate AI tutor response"""
    message_lower = message.lower()
    
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
    
    else:
        return "I'm your AI tutor! I can help with course recommendations, explain concepts, provide study tips, and answer questions. What would you like to know?"


def get_ai_suggestions(message):
    """Get suggested follow-up questions"""
    return [
        "What topics should I focus on next?",
        "Explain this concept in simpler terms",
        "Give me practice exercises",
        "How can I improve my quiz scores?"
    ]


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
def content_upload(request):
    """Upload content files"""
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
    
    # GET request
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
            # Create sample courses with lessons, resources, and quizzes
            os_course, created = Course.objects.get_or_create(
                slug='operating-systems-2',
                defaults={
                    'title': 'Operating Systems 2',
                    'description': 'Advanced OS concepts',
                    'is_published': True
                }
            )
            
            if created:
                # Create lessons
                for i, title in enumerate(['Process Management', 'Memory Systems', 'File Systems'], 1):
                    lesson = Lesson.objects.create(
                        course=os_course,
                        title=title,
                        order=i,
                        content=f'Content for {title}'
                    )
                    
                    # Add resources
                    Resource.objects.create(
                        lesson=lesson,
                        title=f'{title} - Study Notes',
                        kind='note',
                        content=f'Detailed notes for {title}'
                    )
                    
                    # Add quiz
                    quiz = Quiz.objects.create(
                        lesson=lesson,
                        title=f'{title} Quiz',
                        description=f'Test your knowledge of {title}',
                        time_limit=30,
                        pass_score=70
                    )
                    
                    # Add sample questions
                    for j in range(1, 6):
                        question = Question.objects.create(
                            quiz=quiz,
                            text=f'Question {j} about {title}',
                            kind='multiple_choice',
                            order=j
                        )
                        
                        # Add choices
                        for k, choice_text in enumerate(['Option A', 'Option B', 'Option C', 'Option D'], 1):
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=(k == 1)  # First option is correct
                            )
                
                messages.success(request, 'Sample content created successfully!')
            else:
                messages.info(request, 'Sample content already exists.')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'learning/admin/generate_sample.html', {
        'title': 'Generate Sample Content'
    })