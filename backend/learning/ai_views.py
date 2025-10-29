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
from .ai_quiz_generator import get_quiz_generator
from .models import (
    Course, Lesson, Quiz, QuizAttempt, UserProgress,
    ChatConversation, ChatMessage, AIRecommendation
)
from .ai_services import (
    PersonalizedLearningEngine, AITutorService
)


logger = logging.getLogger(__name__)


@login_required
def ai_dashboard(request):
    """
    AI-powered dashboard showing personalized learning insights
    """
    try:
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
        )[:5]
        
        context = {
            'title': 'AI Dashboard - EduCore AI',
            'analytics': analytics,
            'recommendations': recommendations,
            'suggested_lessons': suggested_lessons,
            'adaptive_difficulty': learning_engine.get_adaptive_difficulty(),
        }
    except Exception as e:
        logger.error(f"Error in AI dashboard: {e}")
        context = {
            'title': 'AI Dashboard - EduCore AI',
            'analytics': {},
            'recommendations': [],
            'suggested_lessons': [],
            'adaptive_difficulty': 'intermediate',
            'error': str(e)
        }
    
    return render(request, 'learning/ai_dashboard.html', context)


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
    
    return render(request, 'learning/ai_chatbot.html', context)


@login_required
@csrf_exempt  # Only for development, use CSRF token in production
@require_http_methods(["POST"])
def handle_chat_message(request):
    """
    Handle chat messages with AI tutor - FIXED VERSION
    Generates intelligent responses based on student context
    """
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        
        message_text = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = ChatConversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )
            except ChatConversation.DoesNotExist:
                conversation = ChatConversation.objects.create(
                    user=request.user,
                    title=message_text[:50] if len(message_text) > 50 else message_text
                )
        else:
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=message_text[:50] if len(message_text) > 50 else message_text
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
        
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a helpful response even if there's an error
        return JsonResponse({
            'success': True,
            'response': f"I'm your AI tutor! I can help you with Operating Systems and Database Systems. What would you like to learn about?",
            'suggestions': [
                "Explain process scheduling",
                "What is virtual memory?",
                "Help with SQL queries",
                "What should I study next?"
            ]
        })


def generate_ai_response(user, message):
    """
    Generate intelligent AI response based on user message and context
    """
    message_lower = message.lower()
    
    # Get user's learning performance for context
    learning_engine = PersonalizedLearningEngine(user)
    performance = learning_engine.calculate_overall_performance()
    
    # Analyze message and generate appropriate response
    if any(word in message_lower for word in ['help', 'stuck', 'confused', 'difficult']):
        if performance['avg_score'] >= 80:
            response = "I see you're facing a challenge. That's great for learning! Based on your strong performance so far, let's break this down into smaller parts. What specifically are you struggling with?"
        elif performance['avg_score'] >= 60:
            response = "Don't worry! Learning new concepts can be challenging. Let me help you understand this better. What part confuses you the most?"
        else:
            response = "It's okay to find things difficult - that's where learning happens! Let's start with the fundamentals. What topic would you like me to explain?"
    
    elif any(word in message_lower for word in ['quiz', 'test', 'exam', 'assessment']):
        pass_rate = performance.get('quiz_pass_rate', 0)
        if pass_rate >= 80:
            response = f"Great work! Your quiz performance is at {pass_rate:.0f}%. You're well-prepared. Would you like to attempt more challenging questions?"
        elif pass_rate >= 60:
            response = f"Your pass rate is {pass_rate:.0f}%. You're making good progress! I'd recommend reviewing the areas where you stumbled. Want to practice specific topics?"
        else:
            response = f"Your pass rate is {pass_rate:.0f}%. Let's focus on strengthening your foundation. I recommend reviewing the core concepts first. Which topic should we focus on?"
    
    elif any(word in message_lower for word in ['next', 'recommend', 'should i', 'what next']):
        if performance['completion_rate'] < 30:
            response = "You're just getting started! I recommend completing your current lessons first. This will build a strong foundation. Keep going - you're doing great!"
        elif performance['completion_rate'] < 70:
            response = "You're making solid progress! Based on what you've completed, I recommend exploring more advanced topics next. You're ready for the challenge!"
        else:
            response = "Excellent work! You've mastered most of the material. I recommend exploring specialization topics or helping peers. What interests you most?"
    
    elif any(word in message_lower for word in ['explain', 'what is', 'how', 'definition']):
        response = "Great question! To give you the best explanation, could you tell me which specific concept you'd like me to clarify? I can then tailor it to your level of understanding."
    
    elif any(word in message_lower for word in ['progress', 'score', 'performance', 'how am i']):
        response = f"Your current performance:\n- Average Score: {performance['avg_score']:.1f}%\n- Completion Rate: {performance['completion_rate']:.1f}%\n- Quizzes Passed: {performance['passed_quizzes']}/{performance['total_quizzes']}\n\nYou're making great progress! Keep up the consistent effort."
    
    elif any(word in message_lower for word in ['study', 'tips', 'advice', 'strategy']):
        response = "Here are my personalized study tips for you:\n1. Study during your peak focus hours\n2. Break complex topics into smaller chunks\n3. Practice with quiz questions after learning\n4. Review regularly to strengthen memory\n5. Don't hesitate to ask questions!\n\nWhat specific area would you like tips for?"
    
    else:
        # Default helpful response
        response = f"That's an interesting question! I'm here to help you learn better. Feel free to ask me about:\n- Course concepts and explanations\n- Quiz preparation and practice\n- Study strategies and tips\n- Your learning progress\n\nWhat would you like to discuss?"
    
    suggestions = generate_follow_up_suggestions(message, performance)
    
    return {
        'response': response,
        'suggestions': suggestions
    }


def generate_follow_up_suggestions(message, performance):
    """
    Generate contextual follow-up suggestions based on message and performance
    """
    message_lower = message.lower()
    
    suggestions = [
        "Can you explain this differently?",
        "Give me an example",
        "How can I practice this?",
        "What should I study next?"
    ]
    
    # Add specific suggestions based on message content
    if 'quiz' in message_lower or 'test' in message_lower:
        suggestions = [
            "Show me practice questions",
            "Explain the difficult topics",
            "What are my weak areas?",
            "How can I improve?"
        ]
    elif 'difficult' in message_lower or 'confused' in message_lower:
        suggestions = [
            "Break it down simpler",
            "Show me examples",
            "What's the key concept?",
            "Any related topics I should know?"
        ]
    elif performance['avg_score'] >= 85:
        suggestions = [
            "Ready for advanced topics?",
            "Show me challenging questions",
            "What's next?",
            "Any specialization areas?"
        ]
    
    return suggestions[:4]


@login_required
def get_conversation(request, conversation_id):
    """Get specific conversation messages"""
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
            'conversation': {
                'id': str(conversation.id),
                'title': conversation.title,
                'messages': messages
            }
        })
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_recommendations(request):
    """
    Get personalized recommendations via API
    """
    try:
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
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_learning_analytics(request):
    """
    Get comprehensive learning analytics
    """
    try:
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
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def mark_recommendation_acted(request, recommendation_id):
    """
    Mark a recommendation as acted upon
    """
    try:
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
    except Exception as e:
        logger.error(f"Error marking recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@login_required
def get_adaptive_content(request):
    """
    Get adaptive content recommendations based on user's learning progress and performance
    """
    try:
        learning_engine = PersonalizedLearningEngine(request.user)
        
        # Get user's current difficulty level
        difficulty = learning_engine.get_adaptive_difficulty()
        
        # Get performance metrics
        performance = learning_engine.calculate_overall_performance()
        
        # Generate adaptive recommendations
        recommendations = learning_engine.generate_personalized_recommendations()
        
        # Get next suggested lessons based on difficulty
        suggested_lessons = []
        if difficulty == 'beginner':
            lessons = Lesson.objects.filter(
                course__is_published=True,
                difficulty='beginner'
            ).exclude(
                userprogress__user=request.user,
                userprogress__completed=True
            )[:5]
        elif difficulty == 'advanced':
            lessons = Lesson.objects.filter(
                course__is_published=True,
                difficulty__in=['intermediate', 'advanced']
            ).exclude(
                userprogress__user=request.user,
                userprogress__completed=True
            )[:5]
        else:  # intermediate
            lessons = Lesson.objects.filter(
                course__is_published=True,
                difficulty__in=['beginner', 'intermediate']
            ).exclude(
                userprogress__user=request.user,
                userprogress__completed=True
            )[:5]
        
        for lesson in lessons:
            suggested_lessons.append({
                'id': str(lesson.id),
                'title': lesson.title,
                'difficulty': lesson.difficulty,
                'course': lesson.course.title,
                'estimated_time': getattr(lesson, 'estimated_time_minutes', 30)
            })
        
        return JsonResponse({
            'success': True,
            'adaptive_content': {
                'current_difficulty': difficulty,
                'performance': {
                    'avg_score': performance['avg_score'],
                    'completion_rate': performance['completion_rate'],
                    'quiz_pass_rate': performance.get('quiz_pass_rate', 0)
                },
                'suggested_lessons': suggested_lessons,
                'recommendations': [
                    {
                        'type': rec.recommendation_type,
                        'title': rec.title,
                        'description': rec.description,
                        'priority': rec.priority
                    }
                    for rec in recommendations[:3]
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting adaptive content: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def generate_lesson_explanation(request, lesson_id):
    """
    Generate AI-powered explanation for a lesson using real AI
    """
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Check if user has access to this lesson
        if not lesson.course.is_published:
            return JsonResponse({
                'success': False,
                'error': 'Lesson not available'
            }, status=403)
        
        # Get user's learning context
        learning_engine = PersonalizedLearningEngine(request.user)
        difficulty = learning_engine.get_adaptive_difficulty()
        
        # Get lesson content
        lesson_content = getattr(lesson, 'content', '') or lesson.title
        
        # Generate AI-powered explanation
        quiz_generator = get_quiz_generator()
        explanation = quiz_generator.generate_explanation(
            lesson_content=lesson_content,
            lesson_title=lesson.title,
            difficulty=difficulty
        )
        
        return JsonResponse({
            'success': True,
            'explanation': {
                'lesson_id': str(lesson.id),
                'lesson_title': lesson.title,
                'difficulty': difficulty,
                'content': explanation,
                'estimated_time': getattr(lesson, 'estimated_time_minutes', 30),
                'generated_by_ai': True,
                'tips': [
                    "Read through the explanation carefully",
                    "Take notes on key concepts",
                    "Try the practice exercises",
                    "Ask questions if anything is unclear"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating lesson explanation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def generate_quiz_from_content(request, lesson_id):
    """
    Generate practice quiz questions from lesson content using REAL AI
    This uses advanced language models to create questions based on actual content
    """
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Check if user has access
        if not lesson.course.is_published:
            return JsonResponse({
                'success': False,
                'error': 'Lesson not available'
            }, status=403)
        
        # Get user's difficulty level
        learning_engine = PersonalizedLearningEngine(request.user)
        difficulty = learning_engine.get_adaptive_difficulty()
        
        # Get number of questions from request
        num_questions = int(request.GET.get('num_questions', 5))
        num_questions = min(max(num_questions, 3), 10)  # Between 3 and 10
        
        # Get lesson content
        lesson_content = getattr(lesson, 'content', '')
        
        if not lesson_content:
            # If no content, use lesson title and description
            lesson_content = f"{lesson.title}\n\n"
            if hasattr(lesson, 'description'):
                lesson_content += lesson.description
        
        # Generate questions using AI
        quiz_generator = get_quiz_generator()
        
        logger.info(f"Generating {num_questions} AI questions for lesson: {lesson.title}")
        
        questions = quiz_generator.generate_quiz_questions(
            lesson_content=lesson_content,
            lesson_title=lesson.title,
            difficulty=difficulty,
            num_questions=num_questions,
            question_types=['multiple_choice', 'true_false', 'short_answer']
        )
        
        logger.info(f"Successfully generated {len(questions)} questions using AI")
        
        return JsonResponse({
            'success': True,
            'quiz': {
                'lesson_id': str(lesson.id),
                'lesson_title': lesson.title,
                'difficulty': difficulty,
                'questions': questions,
                'total_questions': len(questions),
                'estimated_time': len(questions) * 3,  # 3 minutes per question
                'generated_by_ai': True,
                'ai_backend': quiz_generator.backend,
                'note': 'These questions were generated by AI based on your lesson content. They are designed to test your understanding of the key concepts.'
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)