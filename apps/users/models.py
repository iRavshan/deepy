from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    # Profile information
    linkedin_url = models.URLField(max_length=255, null=True, blank=True)
    github_url = models.URLField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pcs/', null=True, blank=True)

    # Streak tracking
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Followers and following
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )
    
    @property
    def points(self):
        from apps.challenges.models import Submission, Challenge
        challenge_ids = set(Submission.objects.filter(submitted_by=self, status='accepted').values_list('challenge_id', flat=True))
        challenges = Challenge.objects.filter(id__in=challenge_ids)
        return sum(c.current_score for c in challenges)
    
    def save(self, *args, **kwargs):
        if not self.username:
            while True:
                new_username = f"user{random.randint(1000, 99999)}"
                if not User.objects.filter(username=new_username).exists():
                    self.username = new_username
                    break
        super().save(*args, **kwargs)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email and password are required automatically

    objects = CustomUserManager()

    def __str__(self):
        return self.email
