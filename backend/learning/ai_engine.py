# ============================================
# backend/learning/ai_engine.py (NEW FILE)
# ============================================
"""
AI Engine for Personalized Learning
Analyzes student performance and adapts content difficulty
"""
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import *
import random


class AILearningEngine:
    """AI engine for personalized learning recommendations"""
    
    def __init__(self, user):
        self.user = user
        self.profile, _ = UserProfile.objects.get_or_create(user=user)
    
    def analyze_performance(self, course=None):
        """Analyze student's overall performance"""
        progress_query = UserProgress.objects.filter(user=self.user)
        quiz_query = QuizAttempt.objects.filter(user=self.user)
        
        if course:
            progress_query = progress_query.filter(course=course)
            quiz_query = quiz_query.filter(quiz__lesson__course=course)
        
        # Calculate metrics
        total_progress = progress_query.aggregate(
            avg_completion=Avg('completion_percentage'),
            total_lessons=Count('id'),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        quiz_stats = quiz_query.aggregate(
            avg_score=Avg('score'),
            total_attempts=Count('id'),
            passed=Count('id', filter=Q(is_passed=True))
        )
        
        # Determine performance level
        avg_score = quiz_stats['avg_score'] or 0
        completion_rate = (total_progress['completed'] / total_progress['total_lessons'] * 100) if total_progress['total_lessons'] > 0 else 0
        
        if avg_score >= 85 and completion_rate >= 70:
            level = 'advanced'
        elif avg_score >= 70 and completion_rate >= 50:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        return {
            'level': level,
            'avg_score': avg_score,
            'completion_rate': completion_rate,
            'total_lessons': total_progress['total_lessons'],
            'completed_lessons': total_progress['completed'],
            'quiz_pass_rate': (quiz_stats['passed'] / quiz_stats['total_attempts'] * 100) if quiz_stats['total_attempts'] > 0 else 0,
            'total_quizzes': quiz_stats['total_attempts']
        }
    
    def get_difficulty_level(self, course=None):
        """Determine appropriate difficulty level for student"""
        performance = self.analyze_performance(course)
        
        # Get recent quiz performance (last 5 attempts)
        recent_quizzes = QuizAttempt.objects.filter(
            user=self.user
        ).order_by('-started_at')[:5]
        
        if course:
            recent_quizzes = recent_quizzes.filter(quiz__lesson__course=course)
        
        recent_scores = [attempt.score for attempt in recent_quizzes]
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        # Adaptive difficulty logic
        if recent_avg >= 90:
            return 'hard'
        elif recent_avg >= 75:
            return 'medium'
        elif recent_avg >= 60:
            return 'easy'
        else:
            return 'very_easy'
    
    def generate_recommendations(self, course=None):
        """Generate personalized learning recommendations"""
        performance = self.analyze_performance(course)
        recommendations = []
        
        # Identify weak areas
        weak_lessons = UserProgress.objects.filter(
            user=self.user,
            completion_percentage__lt=50
        ).order_by('completion_percentage')[:3]
        
        if course:
            weak_lessons = weak_lessons.filter(course=course)
        
        for progress in weak_lessons:
            AIRecommendation.objects.get_or_create(
                user=self.user,
                course=progress.course,
                recommendation_type='focus',
                defaults={
                    'title': f'Review {progress.lesson.title}',
                    'description': f'You have {progress.completion_percentage:.0f}% completion. Let\'s strengthen this area.',
                    'priority': 5
                }
            )
        
        # Failed quizzes - need review
        failed_quizzes = QuizAttempt.objects.filter(
            user=self.user,
            is_passed=False
        ).order_by('-started_at')[:2]
        
        if course:
            failed_quizzes = failed_quizzes.filter(quiz__lesson__course=course)
        
        for attempt in failed_quizzes:
            AIRecommendation.objects.get_or_create(
                user=self.user,
                course=attempt.quiz.lesson.course,
                recommendation_type='review',
                defaults={
                    'title': f'Retry {attempt.quiz.title}',
                    'description': f'Previous score: {attempt.score:.0f}%. Review the material and try again.',
                    'priority': 4
                }
            )
        
        # Suggest next lessons
        if performance['level'] in ['intermediate', 'advanced']:
            incomplete_lessons = UserProgress.objects.filter(
                user=self.user,
                is_completed=False
            ).order_by('lesson__order')[:2]
            
            if course:
                incomplete_lessons = incomplete_lessons.filter(course=course)
            
            for progress in incomplete_lessons:
                AIRecommendation.objects.get_or_create(
                    user=self.user,
                    course=progress.course,
                    recommendation_type='next',
                    defaults={
                        'title': f'Continue to {progress.lesson.title}',
                        'description': 'You\'re ready for the next challenge!',
                        'priority': 3
                    }
                )
        
        # Practice recommendations based on performance
        if performance['quiz_pass_rate'] < 70:
            AIRecommendation.objects.get_or_create(
                user=self.user,
                course=course,
                recommendation_type='practice',
                defaults={
                    'title': 'More Practice Needed',
                    'description': 'Complete more quizzes to strengthen your understanding.',
                    'priority': 4
                }
            )
        
        return AIRecommendation.objects.filter(
            user=self.user,
            is_active=True
        ).order_by('-priority', '-created_at')[:5]
    
    def get_adaptive_quiz_questions(self, quiz, num_questions=10):
        """Generate adaptive quiz based on student performance"""
        difficulty = self.get_difficulty_level(quiz.lesson.course)
        
        all_questions = list(quiz.questions.all())
        
        # Weight questions based on difficulty level
        if difficulty == 'very_easy':
            # More basic questions
            selected = random.sample(all_questions, min(num_questions, len(all_questions)))
        elif difficulty == 'easy':
            # Mix of basic and medium
            selected = random.sample(all_questions, min(num_questions, len(all_questions)))
        elif difficulty == 'medium':
            # Standard mix
            selected = random.sample(all_questions, min(num_questions, len(all_questions)))
        else:  # hard
            # More challenging questions
            selected = random.sample(all_questions, min(num_questions, len(all_questions)))
        
        return selected
    
    def predict_time_to_complete(self, lesson):
        """Predict how long student will need for a lesson"""
        performance = self.analyze_performance(lesson.course)
        
        # Base time estimation (minutes)
        base_time = 30
        
        # Adjust based on performance level
        if performance['level'] == 'advanced':
            return base_time * 0.7  # Faster completion
        elif performance['level'] == 'intermediate':
            return base_time
        else:
            return base_time * 1.3  # More time needed
    
    def get_learning_insights(self):
        """Generate learning insights and patterns"""
        progress_data = UserProgress.objects.filter(
            user=self.user
        ).values('last_accessed__hour').annotate(
            count=Count('id')
        ).order_by('-count')
        
        peak_hour = progress_data.first()['last_accessed__hour'] if progress_data else 9
        
        # Determine learning pattern
        if 6 <= peak_hour < 12:
            pattern = 'Morning Learner'
        elif 12 <= peak_hour < 17:
            pattern = 'Afternoon Learner'
        else:
            pattern = 'Evening Learner'
        
        # Get strongest and weakest areas
        course_performance = {}
        for course in Course.objects.filter(is_published=True):
            perf = self.analyze_performance(course)
            course_performance[course.title] = perf['avg_score']
        
        strongest = max(course_performance.items(), key=lambda x: x[1])[0] if course_performance else 'N/A'
        weakest = min(course_performance.items(), key=lambda x: x[1])[0] if course_performance else 'N/A'
        
        return {
            'pattern': pattern,
            'peak_hour': peak_hour,
            'strongest_area': strongest,
            'weakest_area': weakest,
            'learning_velocity': self.calculate_learning_velocity()
        }
    
    def calculate_learning_velocity(self):
        """Calculate how fast student is learning compared to average"""
        last_30_days = timezone.now() - timedelta(days=30)
        
        user_completion = UserProgress.objects.filter(
            user=self.user,
            last_accessed__gte=last_30_days,
            is_completed=True
        ).count()
        
        # Average completion (mock data - replace with actual average)
        avg_completion = 5
        
        if avg_completion > 0:
            velocity = user_completion / avg_completion
            return round(velocity, 1)
        return 1.0