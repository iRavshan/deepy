from django.db import models
from ckeditor.fields import RichTextField
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Tag.objects.get(pk=self.pk)
            if old_instance.name != self.name:
                self.slug = ""

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
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
        if self.pk:
            old_instance = Topic.objects.get(pk=self.pk)
            if old_instance.name != self.name:
                self.slug = ""

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Topic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
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
    input_description = RichTextField(config_name='math_editor', blank=True, null=True)
    output_description = RichTextField(config_name='math_editor', blank=True, null=True)
    sample_tests = models.JSONField(default=list)  
    hidden_tests = models.JSONField(default=list)
    time_limit = models.IntegerField(default=1000)
    memory_limit = models.IntegerField(default=256)

    @property
    def current_score(self):
        import math
        n = self.submissions.filter(status='accepted').values('submitted_by').distinct().count()
        if n == 0:
            return 100
        score = math.floor(100 - 10 * math.log2(n))
        return max(1, score)

    @property
    def solvers_count(self):
        return self.submissions.filter(status='accepted').values('submitted_by').distinct().count()

    @property
    def acceptance_rate(self):
        total = self.submissions.count()
        if total == 0:
            return 0
        accepted = self.submissions.filter(status='accepted').count()
        return int(round((accepted / total) * 100, 1))

    tags = models.ManyToManyField(Tag, related_name="challenges", blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='challenges')

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Challenge.objects.get(pk=self.pk)
            if old_instance.title != self.title:
                self.slug = ""

        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Challenge.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('challenge_detail', kwargs={'slug': self.slug})
    


class ProgrammingLanguage(models.Model):
    judge0_id = models.IntegerField(unique=True, help_text="Judge0 API dagi til ID raqami")
    name = models.CharField(max_length=100)
    monaco_identifier = models.CharField(max_length=50, help_text="Monaco Editor uchun til nomi, masalan: python, javascript, cpp")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Submission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='task_submissions')
    code = models.TextField()
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compilation_error', 'Compilation Error'),
        ('internal_error', 'Internal Error'),
    ], default='pending')
    execution_time = models.FloatField(null=True, blank=True, help_text="Sekundlarda")
    memory_used = models.IntegerField(null=True, blank=True, help_text="KB da")

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.submitted_by.email} for {self.challenge.title} - {self.status}"

class SavedChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user} - {self.challenge}"