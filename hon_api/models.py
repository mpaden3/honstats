from django.db import models
from django_extensions.db.models import TimeStampedModel


class ApiKey(TimeStampedModel):
    cookie = models.CharField(max_length=127, editable=False)

    def __str__(self):
        return self.cookie
