from django.db import models

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Short URL key, e.g. operating-systems")
    description = models.TextField(blank=True)
    cover_color = models.CharField(max_length=7, default="#4361ee", help_text="Hex color like #4361ee")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    # Keep it simple for now: plain text/HTML. (We can add a rich text editor later.)
    content = models.TextField(blank=True, help_text="You can paste HTML or Markdown.")

    class Meta:
        ordering = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} • {self.order}. {self.title}"


class Resource(models.Model):
    """
    Optional attachments per lesson: PDFs, slides, images, etc.
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="resources/")  # stored in MEDIA_ROOT/resources/
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson} • {self.name}"
