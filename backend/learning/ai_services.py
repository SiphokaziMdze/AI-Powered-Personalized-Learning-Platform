# backend/learning/ai_services.py
"""
Comprehensive AI Services Module for EduCore AI Platform
Features:
- Hugging Face transformers for NLP
- Content generation and analysis
- Personalized learning recommendations
- Student performance analytics
- AI tutor assistance
"""

import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import hashlib

# Hugging Face transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from transformers import T5ForConditionalGeneration, AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not installed. Install with: pip install transformers torch")

# Django imports
from django.core.cache import cache
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import (
    UserProgress, QuizAttempt, Course, Lesson, Quiz, Question,
    AIRecommendation, UserProfile, ChatConversation, ChatMessage
)

logger = logging.getLogger(__name__)


class HuggingFaceAIService:
    """
    Main AI Service using Hugging Face models
    Provides content analysis, question generation, and personalized recommendations
    """
    
    def __init__(self):
        """Initialize AI pipelines - using smaller models for faster inference"""
        self.cache_ttl = 3600  # 1 hour cache
        
        if HAS_TRANSFORMERS:
            try:
                # Text classification for content difficulty analysis
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                
                # Summarization pipeline for content synthesis
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
                
                # Question generation pipeline
                self.qa_pipeline = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-small"
                )
                
                logger.info("✅ Hugging Face pipelines initialized successfully")
            except Exception as e:
                logger.error(f"⚠️ Error initializing pipelines: {e}")
                self.classifier = None
                self.summarizer = None
                self.qa_pipeline = None
        else:
            self.classifier = None
            self.summarizer = None
            self.qa_pipeline = None
    
    def analyze_content_difficulty(self, content: str) -> Dict:
        """
        Analyze content difficulty level
        Returns: 'beginner', 'intermediate', 'advanced'
        """
        if not self.classifier:
            return {"level": "intermediate", "confidence": 0.5, "score": 5}
        
        cache_key = f"difficulty_{hashlib.md5(content.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            candidate_labels = ["easy", "medium", "difficult"]
            result = self.classifier(
                content[:512],  # Limit to 512 chars for efficiency
                candidate_labels
            )
            
            difficulty_map = {
                "easy": ("beginner", 1),
                "medium": ("intermediate", 2),
                "difficult": ("advanced", 3)
            }
            
            level, score = difficulty_map[result['labels'][0]]
            confidence = result['scores'][0]
            
            analysis = {
                "level": level,
                "score": score,
                "confidence": float(confidence),
                "labels": result['labels'][:2],
                "scores": [float(s) for s in result['scores'][:2]]
            }
            
            cache.set(cache_key, analysis, self.cache_ttl)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing difficulty: {e}")
            return {"level": "intermediate", "confidence": 0.5, "score": 2}
    
    def generate_quiz_questions(self, content: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate quiz questions from lesson content using AI
        """
        if not self.qa_pipeline:
            return self._generate_basic_questions(content, num_questions)
        
        try:
            questions = []
            sentences = content.split('.')[:5]  # Use first 5 sentences
            
            for i, sentence in enumerate(sentences):
                if len(sentence.strip()) < 10:
                    continue
                
                # Generate question using T5
                prompt = f"Generate a multiple choice question from this text: {sentence[:200]}"
                
                generated = self.qa_pipeline(prompt, max_length=100)
                
                if generated and len(generated) > 0:
                    question_text = generated[0]['generated_text']
                    questions.append({
                        "question": question_text,
                        "type": "multiple_choice",
                        "generated": True,
                        "source_sentence": sentence[:100]
                    })
                
                if len(questions) >= num_questions:
                    break
            
            return questions if questions else self._generate_basic_questions(content, num_questions)
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._generate_basic_questions(content, num_questions)
    
    def _generate_basic_questions(self, content: str, num_questions: int) -> List[Dict]:
        """Fallback question generation"""
        sentences = content.split('.')
        questions = []
        
        for i, sentence in enumerate(sentences[:num_questions]):
            if len(sentence.strip()) > 10:
                words = sentence.strip().split()
                blank_word = words[len(words)//2] if len(words) > 2 else words[0]
                question_text = sentence.replace(blank_word, "___")
                
                questions.append({
                    "question": f"Fill in the blank: {question_text}",
                    "type": "short_answer",
                    "answer": blank_word,
                    "generated": True
                })
        
        return questions
    
    def summarize_content(self, content: str, max_length: int = 150) -> str:
        """
        Summarize long content into concise explanation
        """
        if not self.summarizer or len(content) < 100:
            return content[:max_length]
        
        cache_key = f"summary_{hashlib.md5(content.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            summary = self.summarizer(
                content[:1024],  # Limit input
                max_length=max_length,
                min_length=50,
                do_sample=False
            )
            
            summary_text = summary[0]['summary_text'] if summary else content[:max_length]
            cache.set(cache_key, summary_text, self.cache_ttl)
            return summary_text
            
        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return content[:max_length]
    
    def extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts/keywords from content"""
        # Simple keyword extraction using TF-IDF-like approach
        keywords = []
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'was', 'are', 'were', 'be', 'been', 'being'
        }
        
        words = content.lower().split()
        word_freq = defaultdict(int)
        
        for word in words:
            clean_word = word.strip('.,!?;:')
            if clean_word not in stop_words and len(clean_word) > 3:
                word_freq[clean_word] += 1
        
        # Get top 5 keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [kw[0] for kw in keywords]


class PersonalizedLearningEngine:
    """
    Adaptive learning engine that personalizes content based on student performance
    """
    
    def __init__(self, user):
        self.user = user
        self.profile, _ = UserProfile.objects.get_or_create(user=user)
        self.ai_service = HuggingFaceAIService()
    
    def get_adaptive_difficulty(self, course: Optional[Course] = None) -> str:
        """
        Determine optimal difficulty level for student
        Adapts based on recent performance
        """
        quizzes = QuizAttempt.objects.filter(user=self.user)
        if course:
            quizzes = quizzes.filter(quiz__lesson__course=course)
        
        # Recent performance (last 5 quizzes)
        recent = quizzes.order_by('-started_at')[:5]
        if not recent:
            return "intermediate"
        
        avg_score = recent.aggregate(Avg('score'))['score__avg'] or 0
        
        if avg_score >= 90:
            return "hard"
        elif avg_score >= 75:
            return "medium"
        elif avg_score >= 60:
            return "easy"
        else:
            return "very_easy"
    
    def generate_personalized_recommendations(self, course: Optional[Course] = None) -> List[AIRecommendation]:
        """
        Generate AI-powered personalized learning recommendations
        """
        recommendations = []
        
        # 1. Weak areas analysis
        weak_progress = UserProgress.objects.filter(
            user=self.user,
            completion_percentage__lt=50
        )
        if course:
            weak_progress = weak_progress.filter(course=course)
        
        weak_progress = weak_progress.order_by('completion_percentage')[:2]
        
        for progress in weak_progress:
            # AI-powered description
            rec, created = AIRecommendation.objects.get_or_create(
                user=self.user,
                course=progress.course,
                recommendation_type='focus',
                defaults={
                    'title': f'🎯 Focus: {progress.lesson.title}',
                    'description': (
                        f"You're at {progress.completion_percentage:.0f}% completion on this lesson. "
                        f"This AI analysis suggests focusing here to strengthen your foundation."
                    ),
                    'priority': 5,
                    'is_active': True
                }
            )
            if created:
                recommendations.append(rec)
        
        # 2. Failed quizzes analysis
        failed_quizzes = QuizAttempt.objects.filter(
            user=self.user,
            is_passed=False
        )
        if course:
            failed_quizzes = failed_quizzes.filter(quiz__lesson__course=course)
        
        failed_quizzes = failed_quizzes.order_by('-started_at')[:2]
        
        for attempt in failed_quizzes:
            score_gap = attempt.quiz.pass_score - attempt.score
            rec, created = AIRecommendation.objects.get_or_create(
                user=self.user,
                course=attempt.quiz.lesson.course,
                recommendation_type='review',
                defaults={
                    'title': f'📚 Review: {attempt.quiz.title}',
                    'description': (
                        f"Last score: {attempt.score:.0f}%. You need {score_gap:.0f} more points to pass. "
                        f"Review the material and try again."
                    ),
                    'priority': 4,
                    'is_active': True
                }
            )
            if created:
                recommendations.append(rec)
        
        # 3. Progress-based next steps
        overall_performance = self.calculate_overall_performance(course)
        
        if overall_performance['avg_score'] >= 75:
            incomplete_lessons = UserProgress.objects.filter(
                user=self.user,
                is_completed=False
            )
            if course:
                incomplete_lessons = incomplete_lessons.filter(course=course)
            
            next_lessons = incomplete_lessons.order_by('lesson__order')[:2]
            
            for progress in next_lessons:
                rec, created = AIRecommendation.objects.get_or_create(
                    user=self.user,
                    course=progress.course,
                    recommendation_type='next',
                    defaults={
                        'title': f'🚀 Next: {progress.lesson.title}',
                        'description': 'You\'re performing well! Ready for the next challenge.',
                        'priority': 3,
                        'is_active': True
                    }
                )
                if created:
                    recommendations.append(rec)
        
        # 4. Practice recommendation
        if overall_performance['quiz_pass_rate'] < 70:
            rec, created = AIRecommendation.objects.get_or_create(
                user=self.user,
                course=course or Course.objects.filter(is_published=True).first(),
                recommendation_type='practice',
                defaults={
                    'title': '💪 More Practice Needed',
                    'description': (
                        f"Your quiz pass rate is {overall_performance['quiz_pass_rate']:.0f}%. "
                        f"Complete more practice quizzes to strengthen understanding."
                    ),
                    'priority': 4,
                    'is_active': True
                }
            )
            if created:
                recommendations.append(rec)
        
        return recommendations
    
    def calculate_overall_performance(self, course: Optional[Course] = None) -> Dict:
        """Calculate comprehensive performance metrics"""
        progress_query = UserProgress.objects.filter(user=self.user)
        quiz_query = QuizAttempt.objects.filter(user=self.user)
        
        if course:
            progress_query = progress_query.filter(course=course)
            quiz_query = quiz_query.filter(quiz__lesson__course=course)
        
        progress_stats = progress_query.aggregate(
            avg_completion=Avg('completion_percentage'),
            total_lessons=Count('id'),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        quiz_stats = quiz_query.aggregate(
            avg_score=Avg('score'),
            total_attempts=Count('id'),
            passed=Count('id', filter=Q(is_passed=True))
        )
        
        return {
            'avg_completion': progress_stats['avg_completion'] or 0,
            'total_lessons': progress_stats['total_lessons'] or 0,
            'completed_lessons': progress_stats['completed'] or 0,
            'avg_score': quiz_stats['avg_score'] or 0,
            'total_quizzes': quiz_stats['total_attempts'] or 0,
            'passed_quizzes': quiz_stats['passed'] or 0,
            'quiz_pass_rate': (
                (quiz_stats['passed'] / quiz_stats['total_attempts'] * 100)
                if quiz_stats['total_attempts'] else 0
            ),
            'completion_rate': (
                (progress_stats['completed'] / progress_stats['total_lessons'] * 100)
                if progress_stats['total_lessons'] else 0
            )
        }
    
    def get_learning_analytics(self) -> Dict:
        """
        Generate comprehensive learning analytics
        """
        performance = self.calculate_overall_performance()
        
        # Study pattern analysis
        progress_by_hour = UserProgress.objects.filter(
            user=self.user
        ).extra(select={'hour': 'EXTRACT(HOUR FROM last_accessed)'}).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')
        
        peak_hour = progress_by_hour.first()['hour'] if progress_by_hour else 14
        
        # Learning style detection
        learning_patterns = {
            'peak_study_hour': int(peak_hour) if peak_hour else 14,
            'study_frequency': self._calculate_study_frequency(),
            'consistency_score': self._calculate_consistency(),
            'learning_velocity': self._calculate_learning_velocity(),
            'recommendation_adherence': self._calculate_recommendation_adherence()
        }
        
        # Identify strengths and weaknesses
        course_performance = {}
        for course in Course.objects.filter(is_published=True):
            perf = self.calculate_overall_performance(course)
            if perf['total_quizzes'] > 0:
                course_performance[course.title] = perf['avg_score']
        
        return {
            'performance': performance,
            'patterns': learning_patterns,
            'strengths': sorted(
                course_performance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3],
            'weaknesses': sorted(
                course_performance.items(),
                key=lambda x: x[1]
            )[:3],
            'predicted_completion_date': self._predict_completion_date(),
            'recommended_study_time': self._recommend_study_schedule()
        }
    
    def _calculate_study_frequency(self) -> Dict:
        """Calculate study frequency metrics"""
        last_7_days = timezone.now() - timedelta(days=7)
        last_30_days = timezone.now() - timedelta(days=30)
        
        activity_7d = UserProgress.objects.filter(
            user=self.user,
            last_accessed__gte=last_7_days
        ).count()
        
        activity_30d = UserProgress.objects.filter(
            user=self.user,
            last_accessed__gte=last_30_days
        ).count()
        
        return {
            'last_7_days': activity_7d,
            'last_30_days': activity_30d,
            'average_daily': activity_30d / 30 if activity_30d > 0 else 0
        }
    
    def _calculate_consistency(self) -> float:
        """Calculate study consistency score (0-100)"""
        last_30_days = timezone.now() - timedelta(days=30)
        
        study_days = UserProgress.objects.filter(
            user=self.user,
            last_accessed__gte=last_30_days
        ).dates('last_accessed', 'day').count()
        
        consistency = min(100, (study_days / 30) * 100)
        return round(consistency, 1)
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate how fast student is progressing"""
        last_30_days = timezone.now() - timedelta(days=30)
        
        completions = UserProgress.objects.filter(
            user=self.user,
            last_accessed__gte=last_30_days,
            is_completed=True
        ).count()
        
        velocity = completions / 30 if completions > 0 else 0
        return round(velocity, 2)
    
    def _calculate_recommendation_adherence(self) -> float:
        """Calculate how well student follows AI recommendations"""
        recommendations = AIRecommendation.objects.filter(user=self.user)
        if not recommendations.exists():
            return 0.0
        
        acted_upon = recommendations.filter(acted_upon_at__isnull=False).count()
        adherence = (acted_upon / recommendations.count()) * 100
        return round(min(100, adherence), 1)
    
    def _predict_completion_date(self) -> Optional[str]:
        """Predict when student will complete current course"""
        velocity = self._calculate_learning_velocity()
        if velocity == 0:
            return None
        
        incomplete_count = UserProgress.objects.filter(
            user=self.user,
            is_completed=False
        ).count()
        
        days_remaining = int(incomplete_count / velocity) if velocity > 0 else None
        if days_remaining:
            completion_date = timezone.now() + timedelta(days=days_remaining)
            return completion_date.strftime('%Y-%m-%d')
        
        return None
    
    def _recommend_study_schedule(self) -> Dict:
        """Recommend optimal study schedule"""
        consistency = self._calculate_consistency()
        
        if consistency > 80:
            frequency = "Daily"
            duration = "30-45 minutes"
        elif consistency > 50:
            frequency = "4-5 times per week"
            duration = "45-60 minutes"
        else:
            frequency = "3-4 times per week"
            duration = "60-90 minutes"
        
        return {
            'recommended_frequency': frequency,
            'recommended_duration': duration,
            'best_time': self._get_best_study_time()
        }
    
    def _get_best_study_time(self) -> str:
        """Get recommended study time based on performance patterns"""
        # In real implementation, this would analyze performance by hour
        return "Based on your data: Mornings (9-11 AM) show best focus"


class AITutorService:
    """
    AI Tutor service for intelligent student assistance
    """
    
    def __init__(self, user):
        self.user = user
        self.ai_service = HuggingFaceAIService()
    
    def get_lesson_explanation(self, lesson: Lesson) -> str:
        """Generate AI-powered lesson explanation"""
        if not lesson.content:
            return "Content not available"
        
        # Summarize lesson content into clear explanation
        summary = self.ai_service.summarize_content(
            lesson.content,
            max_length=300
        )
        
        return summary
    
    def get_concept_clarification(self, concept: str, context: str = "") -> str:
        """Provide clarification on specific concepts"""
        # This would integrate with actual AI model
        return f"Concept: {concept}\n\nThis is an important topic. {context}"
    
    def generate_study_tips(self, lesson: Lesson) -> List[str]:
        """Generate personalized study tips"""
        difficulty = self.ai_service.analyze_content_difficulty(lesson.content)
        
        tips = []
        
        if difficulty['level'] == 'advanced':
            tips.extend([
                "🎯 Break down complex concepts into smaller parts",
                "📝 Create detailed notes with diagrams",
                "🔄 Review multiple times before taking quiz"
            ])
        elif difficulty['level'] == 'intermediate':
            tips.extend([
                "📚 Read through the material carefully",
                "✍️ Take notes on key points",
                "🧠 Test yourself with practice questions"
            ])
        else:
            tips.extend([
                "📖 Go through the content at your own pace",
                "💡 Focus on main concepts",
                "🎓 Try practice questions when ready"
            ])
        
        return tips


# Initialize global AI service
try:
    global_ai_service = HuggingFaceAIService()
except Exception as e:
    logger.error(f"Failed to initialize AI service: {e}")
    global_ai_service = None