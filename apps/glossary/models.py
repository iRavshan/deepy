from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db import models


class Term(models.Model):
    term = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    short_definition = models.CharField(max_length=255)
    definition = RichTextField()

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