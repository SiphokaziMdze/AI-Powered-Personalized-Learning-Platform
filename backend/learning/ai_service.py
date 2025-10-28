#backend/learning/ai_service.py
import google.generativeai as genai
from django.conf import settings
from .models import UserProgress, QuizAttempt, Course
from datetime import datetime

class GeminiAIService:
    """Service to interact with Google Gemini AI"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Start chat session
        self.chat = None
    
    def get_user_context(self, user):
        """Get user's learning context for personalized responses"""
        # Get user's courses
        user_courses = Course.objects.filter(
            lessons__userprogress__user=user
        ).distinct()
        
        # Get recent quiz performance
        recent_quizzes = QuizAttempt.objects.filter(
            user=user
        ).order_by('-started_at')[:5]
        
        # Get completion stats
        total_progress = UserProgress.objects.filter(
            user=user
        ).count()
        
        completed = UserProgress.objects.filter(
            user=user,
            is_completed=True
        ).count()
        
        context = f"""
User Profile:
- Enrolled Courses: {', '.join([c.title for c in user_courses]) if user_courses else 'None'}
- Lessons Completed: {completed}/{total_progress}
- Recent Quiz Scores: {', '.join([f'{q.score:.0f}%' for q in recent_quizzes]) if recent_quizzes else 'No quizzes taken'}

You are an AI tutor for EduCore AI, helping students learn Operating Systems and Database Systems.
Be helpful, encouraging, and provide clear explanations. If asked about topics outside these courses,
politely redirect to the course materials.
"""
        return context
    
    def chat_with_ai(self, user, message, chat_history=None):
        """Send message to Gemini and get response"""
        try:
            # Get user context
            user_context = self.get_user_context(user)
            
            # Create system prompt
            system_prompt = f"""
{user_context}

Guidelines:
- Be a helpful, patient, and encouraging tutor
- Provide clear, concise explanations
- Use examples when explaining concepts
- Ask follow-up questions to ensure understanding
- If the student is struggling, break down concepts into simpler parts
- Celebrate their progress and achievements
- Focus on Operating Systems and Database topics
"""
            
            # Start new chat with history if provided
            if chat_history:
                # Convert chat history to Gemini format
                history = []
                for msg in chat_history:
                    history.append({
                        "role": "user" if msg['role'] == 'user' else "model",
                        "parts": [msg['content']]
                    })
                
                self.chat = self.model.start_chat(history=history)
            else:
                # Start fresh chat with system prompt
                self.chat = self.model.start_chat(history=[])
                # Send system prompt as first message
                self.chat.send_message(system_prompt)
            
            # Send user message
            response = self.chat.send_message(message)
            
            return {
                'success': True,
                'response': response.text,
                'suggestions': self._generate_suggestions(message)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': "I'm having trouble connecting right now. Please try again in a moment."
            }
    
    def _generate_suggestions(self, last_message):
        """Generate follow-up question suggestions"""
        suggestions = [
            "Can you explain this concept in simpler terms?",
            "Can you give me an example?",
            "What should I study next?",
            "How can I improve my understanding?"
        ]
        
        # Add context-specific suggestions
        if "process" in last_message.lower():
            suggestions.insert(0, "Tell me more about process scheduling")
        elif "memory" in last_message.lower():
            suggestions.insert(0, "Explain virtual memory")
        elif "database" in last_message.lower() or "sql" in last_message.lower():
            suggestions.insert(0, "Help me with SQL queries")
        
        return suggestions[:4]  # Return max 4 suggestions