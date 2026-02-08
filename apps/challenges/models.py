from django.db import models
from ckeditor.fields import RichTextField
from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class Topic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Topic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class Hint(models.Model):
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE, related_name='hints')
    text = RichTextField(config_name='math_editor',)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('challenge', 'order')

    def save(self, *args, **kwargs):
        if not self.order or self.order == 0:
            last_hint = Hint.objects.filter(challenge=self.challenge).order_by('-order').first()
            self.order = (last_hint.order + 1) if last_hint else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hint {self.order} for {self.challenge.title}"
    


class Challenge(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    description = RichTextField(config_name='math_editor', blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ])
    input_description = RichTextField(config_name='math_editor', blank=True, null=True)
    output_description = RichTextField(config_name='math_editor', blank=True, null=True)
    sample_tests = models.JSONField(default=list)  
    hidden_tests = models.JSONField(default=list)
    time_limit = models.FloatField(default=1.0)
    time_limit = models.FloatField(default=1.0)
    memory_limit = models.IntegerField(default=256)

    tags = models.ManyToManyField(Tag, related_name="challenges", blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='challenges')

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Challenge.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class Submission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='task_submissions')
    code = models.TextField()
    language = models.CharField(max_length=50, choices=[
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("cpp", "C++"),
    ])
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
    ], default='pending')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.submitted_by.email} for {self.task.title} - {self.status}"

class SavedChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user} - {self.challenge}"