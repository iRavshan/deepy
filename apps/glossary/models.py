from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db import models
from django.conf import settings


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji or icon character")
    
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


class Term(models.Model):
    term = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    short_definition = models.CharField(max_length=255)
    definition = RichTextField(null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='terms')

    class Meta:
        ordering = ['term']

    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.term)
            slug = base_slug
            counter = 1

            while Term.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.term

class SavedTerm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_terms')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'term')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user} - {self.term}"