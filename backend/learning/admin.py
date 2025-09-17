from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Course, Lesson, Resource


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    inlines = [ResourceInline]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "lesson", "created_at")
    search_fields = ("name", "lesson__title")
