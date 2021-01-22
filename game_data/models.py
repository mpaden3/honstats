from django.db import models
from django_extensions.db.models import TimeStampedModel


class Hero(TimeStampedModel):
    hero_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)


class Item(TimeStampedModel):
    item_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
