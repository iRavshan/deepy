from django.db import models
from django.conf import settings
from django.utils.text import slugify
from ckeditor.fields import RichTextField



class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField()
    level = models.CharField(max_length=50, choices=[
        ('beginner', "Boshlang'ich"),
        ('intermediate', "O'rta"),
        ('advanced', "Murakkab"),
    ])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class LearningDetail(models.Model):
    course = models.ForeignKey(Course, related_name='learning_details', on_delete=models.CASCADE)
    text = RichTextField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text



class Section(models.Model):
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Section.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} / {self.title}"




class Lesson(models.Model):
    section = models.ForeignKey(Section, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    speech = models.TextField()  
    content = RichTextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['section', 'order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Lesson.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section.title}: {self.title}"
    


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"
    


class LessonProgress(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'lesson')
        ordering = ['lesson']

    def __str__(self):
        return f"{self.user} - {self.lesson} - {'Done' if self.completed else 'Not done'}"
    


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')

    def __str__(self):
        return f"Quiz for {self.lesson.title}"
    

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = RichTextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]
    

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = RichTextField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    

class QuizAttempt(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz}"