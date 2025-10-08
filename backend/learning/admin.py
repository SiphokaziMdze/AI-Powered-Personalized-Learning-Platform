# backend/learning/admin.py
from django.contrib import admin
from .models import *

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'created_at')
    list_filter = ('course', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('course', 'order')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'kind', 'created_at')
    list_filter = ('kind', 'created_at', 'lesson__course')
    search_fields = ('title', 'content')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'is_active', 'time_limit', 'pass_score')
    list_filter = ('is_active', 'lesson__course')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'quiz', 'kind', 'points', 'order')
    list_filter = ('kind', 'quiz__lesson__course')
    search_fields = ('text',)
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_preview', 'is_correct')
    list_filter = ('is_correct', 'question__quiz__lesson__course')
    search_fields = ('text',)
    
    def question_preview(self, obj):
        return obj.question.text[:30] + "..." if len(obj.question.text) > 30 else obj.question.text
    question_preview.short_description = 'Question'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'study_streak', 'preferred_learning_style')
    list_filter = ('preferred_learning_style', 'timezone', 'notifications_enabled')
    search_fields = ('user__username', 'user__email', 'location')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'lesson', 'completion_percentage', 'is_completed', 'last_accessed')
    list_filter = ('is_completed', 'course', 'last_accessed')
    search_fields = ('user__username', 'course__title', 'lesson__title')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'is_passed', 'started_at')
    list_filter = ('is_passed', 'quiz__lesson__course', 'started_at')
    search_fields = ('user__username', 'quiz__title')

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'recommendation_type', 'title', 'priority', 'is_active', 'created_at')
    list_filter = ('recommendation_type', 'priority', 'is_active', 'course')
    search_fields = ('user__username', 'title', 'description')