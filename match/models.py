from django.db import models
from django_extensions.db.models import TimeStampedModel
from account.models import Account
from game_data.models import Hero


class Match(TimeStampedModel):
    FETCHED = "1"
    API = "2"
    REPLAY = "3"
    PARSED_LEVELS = [
        (FETCHED, "Fetched"),
        (API, "Api"),
        (REPLAY, "Replay"),
    ]
    match_id = models.IntegerField(primary_key=True)
    match_date = models.DateField()
    parsed_level = models.TextField(
        max_length=1, choices=PARSED_LEVELS, default=FETCHED
    )


class Player(TimeStampedModel):
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    hero = models.ForeignKey(Hero, on_delete=models.DO_NOTHING)
    gpm = models.FloatField()
