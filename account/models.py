from django.db import models
from django_extensions.db.models import TimeStampedModel


class Account(TimeStampedModel):
    account_id = models.IntegerField(primary_key=True)
    nickname = models.CharField(max_length=128, null=True)
    super_id = models.IntegerField(null=True)
    games_played = models.IntegerField(null=True)
    total_games_played = models.IntegerField(null=True)
    create_date = models.DateField(null=True)
    last_activity = models.DateField(null=True)

    def __str__(self):
        return self.nickname
