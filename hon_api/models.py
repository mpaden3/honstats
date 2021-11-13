from django.db import models
from django_extensions.db.models import TimeStampedModel


class ApiKey(TimeStampedModel):
    cookie = models.CharField(max_length=127)
    username = models.CharField(max_length=255, editable=False, null=True)
    password = models.CharField(max_length=255, editable=False, null=True)

    def __str__(self):
        return self.cookie
