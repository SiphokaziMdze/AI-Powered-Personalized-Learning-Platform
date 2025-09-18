# backend/learning/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Course, Lesson, Quiz, Question, Attempt
from django.contrib import messages

@login_required
def course_list(request):
    """List all available courses"""
    courses = Course.objects.filter(is_published=True)
    context = {
        'title': 'Courses - OS2 Learn',
        'courses': courses
    }
    return render(request, 'learning/course_list.html', context)

@login_required
def course_detail(request, slug):
    """Course detail view with lessons"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.all()
    
    context = {
        'title': f'{course.title} - OS2 Learn',
        'course': course,
        'lessons': lessons
    }
    return render(request, 'learning/course_detail.html', context)

@login_required
def lesson_detail(request, lesson_id):
    """Individual lesson view"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    resources = lesson.resources.all()
    
    # Mark as accessed (you can extend this logic)
    from .models import LessonProgress
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': False}
    )
    progress.save()  # Updates last_accessed
    
    context = {
        'title': f'{lesson.title} - OS2 Learn',
        'lesson': lesson,
        'resources': resources,
        'progress': progress
    }
    return render(request, 'learning/lesson_detail.html', context)

@login_required
def take_quiz(request, quiz_id):
    """Take a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        # Process quiz submission
        attempt = Attempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=0  # Calculate based on answers
        )
        
        # Process answers and calculate score
        # This is a simplified version - you'd implement full scoring logic
        
        messages.success(request, f'Quiz completed! Your score: {attempt.score}%')
        return redirect('learning:quiz_list')
    
    context = {
        'title': f'{quiz.title} - OS2 Learn',
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'learning/take_quiz.html', context)

@login_required
def quiz_list(request):
    """List available quizzes"""
    quizzes = Quiz.objects.filter(is_active=True)
    user_attempts = Attempt.objects.filter(user=request.user)
    
    context = {
        'title': 'Quizzes - OS2 Learn',
        'quizzes': quizzes,
        'user_attempts': user_attempts
    }
    return render(request, 'learning/quiz_list.html', context)

@login_required
def flashcards(request):
    """Flashcard review system"""
    context = {
        'title': 'Flashcards - OS2 Learn',
        'message': 'Flashcard system coming soon!'
    }
    return render(request, 'learning/flashcards.html', context)

@login_required
def ask_ai(request):
    """AI Tutor interface"""
    context = {
        'title': 'AI Tutor - OS2 Learn',
        'message': 'AI Tutor system coming soon!'
    }
    return render(request, 'learning/ask_ai.html', context)