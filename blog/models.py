from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
