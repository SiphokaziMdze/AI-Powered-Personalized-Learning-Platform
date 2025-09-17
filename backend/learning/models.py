# backend/learning/models.py
from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(TimeStampedModel):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Lesson(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1, db_index=True)
    # keep your content field if you had one:
    content = models.TextField(blank=True)

    class Meta:
        ordering = ["course", "order"]
        unique_together = [("course", "order")]

    def __str__(self):
        return f"{self.course.title} — {self.order}. {self.title}"


class Resource(TimeStampedModel):
    class Type(models.TextChoices):
        NOTE = "note", "Note/Article"
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF"
        LINK = "link", "External Link"
        SLIDE = "slide", "Slide Deck"
        IMAGE = "image", "Image"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=Type.choices, default=Type.NOTE)
    # for uploaded files (PDFs, slides, images, videos if small). Use MEDIA settings.
    file = models.FileField(upload_to="resources/%Y/%m/", blank=True, null=True)
    # for an external URL (YouTube, docs, etc.)
    url = models.URLField(blank=True, null=True)
    # optional text content
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.kind})"


# --- Users / Enrollment / Progress ---

class StudentProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=120, blank=True)
    learning_style = models.CharField(
        max_length=50,
        choices=[
            ("visual", "Visual"),
            ("auditory", "Auditory"),
            ("reading", "Reading/Writing"),
            ("kinesthetic", "Kinesthetic"),
        ],
        default="visual",
    )

    def __str__(self):
        return self.display_name or self.user.get_username()


class Enrollment(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "course")]
        indexes = [
            models.Index(fields=["user", "course"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


class LessonProgress(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0-100
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "lesson")]
        indexes = [
            models.Index(fields=["user", "lesson"]),
        ]

    def __str__(self):
        status = "✓" if self.completed else "…"
        return f"{self.user.username} / {self.lesson} ({status})"


# --- Quizzes / Attempts ---

class Quiz(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200, default="Lesson Quiz")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} — {self.lesson}"


class Question(TimeStampedModel):
    class Kind(models.TextChoices):
        MCQ = "mcq", "Multiple Choice"
        TRUE_FALSE = "tf", "True/False"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.MCQ)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"Q: {self.text[:60]}"


class Choice(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        label = "✓" if self.is_correct else "•"
        return f"{label} {self.text[:60]}"


class Attempt(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0–100
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.quiz} ({self.score})"
