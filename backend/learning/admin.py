# backend/learning/admin.py
from django.contrib import admin
from .models import (
    Course, Lesson, Resource,
    StudentProfile, Enrollment, LessonProgress,
    Quiz, Question, Choice, Attempt
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    list_filter = ("is_published",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order")

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "kind", "created_at")
    list_filter = ("kind", "lesson__course")
    search_fields = ("title", "lesson__title")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "learning_style", "created_at")
    list_filter = ("learning_style",)
    search_fields = ("user__username", "display_name")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "active", "started_at")
    list_filter = ("active", "course")
    search_fields = ("user__username", "course__title")

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "score", "updated_at")
    list_filter = ("completed", "lesson__course")

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "is_active", "created_at")
    list_filter = ("is_active", "lesson__course")
    inlines = [QuestionInline]

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "started_at", "finished_at")
    list_filter = ("quiz__lesson__course",)
