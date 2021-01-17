from django.db import models
from django_extensions.db.models import TimeStampedModel


class Account(TimeStampedModel):
    account_id = models.IntegerField(primary_key=True)
    nickname = models.CharField(max_length=128)
    super_id = models.IntegerField()
    games_played = models.IntegerField()
    total_games_played = models.IntegerField()
    create_date = models.DateField()
    last_activity = models.DateField()
