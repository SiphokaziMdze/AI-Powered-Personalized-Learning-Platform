# backend/learning/ai_views.py
"""
AI-Powered Views for EduCore AI Platform
Handles AI chatbot, personalized dashboard, recommendations, and adaptive learning
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import (
    Course, Lesson, Quiz, QuizAttempt, UserProgress,
    ChatConversation, ChatMessage, AIRecommendation
)
from .ai_services import (
    PersonalizedLearningEngine, AITutorService, HuggingFaceAIService,
    global_ai_service
)

logger = logging.getLogger(__name__)


@login_required
def ai_dashboard(request):
    """
    AI-powered dashboard showing personalized learning insights
    """
    learning_engine = PersonalizedLearningEngine(request.user)
    
    # Get analytics
    analytics = learning_engine.get_learning_analytics()
    
    # Get personalized recommendations
    recommendations = learning_engine.generate_personalized_recommendations()
    
    # Get suggested next lessons
    suggested_lessons = Lesson.objects.filter(
        course__is_published=True
    ).exclude(
        userprogress__user=request.user
    ).annotate(
        difficulty=Avg('quiz__pass_score')
    )[:5]
    
    context = {
        'title': 'AI Dashboard - EduCore AI',
        'analytics': analytics,
        'recommendations': recommendations,
        'suggested_lessons': suggested_lessons,
        'adaptive_difficulty': learning_engine.get_adaptive_difficulty(),
    }
    
    return render(request, 'ai_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def ai_chatbot(request):
    """
    AI Chatbot for student assistance
    GET: Display chatbot interface
    POST: Process chat messages
    """
    if request.method == 'POST':
        return handle_chat_message(request)
    
    # GET: Show chatbot interface
    conversations = ChatConversation.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:5]
    
    context = {
        'title': 'AI Tutor - EduCore AI',
        'conversations': conversations,
    }
    
    return render(request, 'ai_chatbot.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def handle_chat_message(request):
    """
    Handle chat messages with AI tutor
    Uses Gemini API with Hugging Face for enhanced analysis
    """
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Get or create conversation
        if conversation_id:
            conversation = ChatConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        else:
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=message_text[:50]
            )
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message_text
        )
        
        # Generate AI response
        ai_response = generate_ai_response(request.user, message_text)
        
        # Save AI message
        ai_msg = ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response['response']
        )
        
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'response': ai_response['response'],
            'suggestions': ai_response.get('suggestions', []),
            'conversation_id': str(conversation.id),
            'message_id': str(ai_msg.id)
        })
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_ai_response(user, message):
    """
    Generate AI response using combined AI techniques
    """
    tutor_service = AITutorService(user)
    learning_engine = PersonalizedLearningEngine(user)
    
    # Analyze user message
    keywords = extract_keywords(message)
    
    # Context awareness
    user_performance = learning_engine.calculate_overall_performance()
    
    # Generate response based on message type
    if any(word in message.lower() for word in ['help', 'explain', 'what is', 'how']):
        response = generate_explanation_response(message, keywords)
    elif any(word in message.lower() for word in ['next', 'recommend', 'should i', 'what should']):
        response = generate_recommendation_response(user, learning_engine)
    elif any(word in message.lower() for word in ['quiz', 'test', 'score', 'pass']):
        response = generate_study_response(message, learning_engine)
    else:
        response = generate_general_response(message, user_performance)
    
    # Generate suggestions
    suggestions = generate_follow_up_suggestions(message, keywords)
    
    return {
        'response': response,
        'suggestions': suggestions
    }


def extract_keywords(text):
    """Extract keywords from message"""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'
    }
    
    words = text.lower().split()
    keywords = [w.strip('.,!?;:') for w in words 
                if w.lower() not in stop_words and len(w) > 3]
    return keywords[:5]


def generate_explanation_response(message, keywords):
    """Generate explanatory response"""
    ai_service = HuggingFaceAIService()
    
    responses = {
        'process': "A process is a program in execution. It includes the program code, data, and system resources.",
        'memory': "Memory management handles allocation and deallocation of memory for processes.",
        'database': "A database is an organized collection of structured data.",
        'sql': "SQL (Structured Query Language) is used to interact with relational databases.",
        'schedule': "Process scheduling determines which process runs on the CPU at any given time.",
    }
    
    for keyword in keywords:
        if keyword in responses:
            return responses[keyword]
    
    return (
        f"Great question about {', '.join(keywords)}! "
        "I'd recommend reviewing the lesson material and then trying some practice questions. "
        "What specific aspect would you like me to clarify?"
    )


def generate_recommendation_response(user, learning_engine):
    """Generate personalized recommendation"""
    performance = learning_engine.calculate_overall_performance()
    
    if performance['avg_score'] >= 85:
        return (
            "🌟 You're doing great! I recommend moving to the next advanced topic. "
            "Would you like me to suggest the best next lesson for you?"
        )
    elif performance['avg_score'] >= 70:
        return (
            "📚 You're progressing well! I recommend practicing with more quiz questions "
            "to strengthen your understanding of the current material."
        )
    else:
        return (
            "💪 Keep going! I recommend reviewing the fundamentals and taking practice quizzes. "
            "Would you like tips on studying this material more effectively?"
        )


def generate_study_response(message, learning_engine):
    """Generate study-related response"""
    performance = learning_engine.calculate_overall_performance()
    
    tips = [
        "🎯 Focus on one concept at a time",
        "📝 Take detailed notes while studying",
        "🧪 Practice with quiz questions",
        "🔄 Review material multiple times",
        "💡 Relate concepts to real-world examples"
    ]
    
    return (
        f"Your current pass rate is {performance['quiz_pass_rate']:.0f}%. "
        f"Here are some study tips:\n\n" + "\n".join(tips[:3]) +
        "\n\nWould you like specific help with any topic?"
    )


def generate_general_response(message, performance):
    """Generate general conversational response"""
    if performance['avg_score'] > 0:
        return (
            f"That's a good question! Based on your learning progress "
            f"(current score: {performance['avg_score']:.0f}%), "
            f"I can help you understand complex concepts better. "
            f"What would you like to focus on?"
        )
    else:
        return (
            "Welcome! I'm here to help you learn. You can ask me to explain concepts, "
            "recommend what to study next, or help with quiz preparation. What would you like help with?"
        )


def generate_follow_up_suggestions(message, keywords):
    """Generate contextual follow-up suggestions"""
    suggestions = [
        "Can you explain this in simpler terms?",
        "Can you give me an example?",
        "How does this apply in practice?",
        "What should I study next?",
    ]
    
    # Add keyword-specific suggestions
    for keyword in keywords:
        if 'process' in keyword:
            suggestions.insert(0, "Tell me about process scheduling")
        elif 'memory' in keyword:
            suggestions.insert(0, "Explain virtual memory")
        elif 'database' in keyword or 'sql' in keyword:
            suggestions.insert(0, "Help me with SQL queries")
    
    return suggestions[:4]


@login_required
def get_conversation(request, conversation_id):
    """Get specific conversation messages"""
    conversation = get_object_or_404(
        ChatConversation,
        id=conversation_id,
        user=request.user
    )
    
    messages = conversation.messages.all().values('role', 'content', 'created_at')
    
    return JsonResponse({
        'success': True,
        'conversation': {
            'id': str(conversation.id),
            'title': conversation.title,
            'messages': list(messages)
        }
    })


@login_required
def get_recommendations(request):
    """
    Get personalized recommendations via API
    """
    course_id = request.GET.get('course_id')
    course = None
    
    if course_id:
        course = get_object_or_404(Course, id=course_id)
    
    learning_engine = PersonalizedLearningEngine(request.user)
    recommendations = learning_engine.generate_personalized_recommendations(course)
    
    return JsonResponse({
        'success': True,
        'recommendations': [
            {
                'id': str(rec.id),
                'type': rec.recommendation_type,
                'title': rec.title,
                'description': rec.description,
                'priority': rec.priority,
            }
            for rec in recommendations
        ]
    })


@login_required
def get_learning_analytics(request):
    """
    Get comprehensive learning analytics
    """
    learning_engine = PersonalizedLearningEngine(request.user)
    analytics = learning_engine.get_learning_analytics()
    
    return JsonResponse({
        'success': True,
        'analytics': {
            'performance': analytics['performance'],
            'patterns': analytics['patterns'],
            'predicted_completion': analytics.get('predicted_completion_date'),
            'study_recommendation': analytics['recommended_study_time']
        }
    })


@login_required
def generate_lesson_explanation(request, lesson_id):
    """
    Generate AI explanation for a lesson
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    tutor_service = AITutorService(request.user)
    
    explanation = tutor_service.get_lesson_explanation(lesson)
    study_tips = tutor_service.generate_study_tips(lesson)
    
    return JsonResponse({
        'success': True,
        'explanation': explanation,
        'study_tips': study_tips,
        'lesson': {
            'id': str(lesson.id),
            'title': lesson.title,
        }
    })


@login_required
def generate_quiz_from_content(request, lesson_id):
    """
    Generate quiz questions from lesson content using AI
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if not global_ai_service:
        return JsonResponse({
            'success': False,
            'error': 'AI service not available'
        }, status=503)
    
    try:
        questions = global_ai_service.generate_quiz_questions(
            lesson.content,
            num_questions=5
        )
        
        return JsonResponse({
            'success': True,
            'questions': questions,
            'lesson': {
                'id': str(lesson.id),
                'title': lesson.title
            }
        })
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_adaptive_content(request):
    """
    Get content adapted to student's level
    """
    learning_engine = PersonalizedLearningEngine(request.user)
    
    # Get courses and adapt difficulty
    courses = Course.objects.filter(is_published=True)
    
    adapted_courses = []
    for course in courses:
        difficulty = learning_engine.get_adaptive_difficulty(course)
        adapted_courses.append({
            'id': str(course.id),
            'title': course.title,
            'suggested_difficulty': difficulty,
            'description': course.description
        })
    
    return JsonResponse({
        'success': True,
        'courses': adapted_courses,
        'recommended_next_course': adapted_courses[0] if adapted_courses else None
    })


@login_required
def mark_recommendation_acted(request, recommendation_id):
    """
    Mark a recommendation as acted upon
    """
    recommendation = get_object_or_404(
        AIRecommendation,
        id=recommendation_id,
        user=request.user
    )
    
    recommendation.acted_upon_at = timezone.now()
    recommendation.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Recommendation marked as acted upon'
    })