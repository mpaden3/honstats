from django.db import models
from django_extensions.db.models import TimeStampedModel
from account.models import Account
from game_data.models import Hero

TEAM_EMPTY = "0"
TEAM_RADIANT = "1"
TEAM_DIRE = "2"


class Match(TimeStampedModel):
    FETCHED = "1"
    API = "2"
    REPLAY = "3"
    PARSED_LEVELS = [
        (FETCHED, "FETCHED"),
        (API, "API"),
        (REPLAY, "REPLAY"),
    ]
    WINNING_TEAM = [
        (TEAM_EMPTY, "Empty"),
        (TEAM_RADIANT, "Radiant"),
        (TEAM_DIRE, "Dire"),
    ]

    match_id = models.IntegerField(primary_key=True)
    match_date = models.DateField()
    match_name = models.CharField(max_length=127)
    replay_log_url = models.CharField(max_length=511)
    winning_team = models.TextField(
        max_length=1, choices=WINNING_TEAM, default=TEAM_EMPTY
    )
    parsed_level = models.TextField(
        max_length=1, choices=PARSED_LEVELS, default=FETCHED
    )

    def __str__(self):
        if self.match_name:
            return self.match_name
        return str(self.match_id)


class Player(TimeStampedModel):
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    account = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="matches"
    )
    TEAM = [
        (TEAM_EMPTY, "Empty"),
        (TEAM_RADIANT, "Radiant"),
        (TEAM_DIRE, "Dire"),
    ]
    team = models.TextField(max_length=1, choices=TEAM, default=TEAM_EMPTY)
    position = models.TextField(max_length=1, null=True)
    level = models.IntegerField(null=True)
    hero = models.ForeignKey(Hero, on_delete=models.DO_NOTHING, null=True)
    hero_kills = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    kicked = models.BooleanField(default=False)
    hero_assists = models.IntegerField(null=True)
    networth = models.IntegerField(null=True)
    hero_damage = models.IntegerField(null=True)
    lasthits = models.IntegerField(null=True)
    denies = models.IntegerField(null=True)
    wards = models.IntegerField(null=True)
    mmr_before = models.FloatField(null=True)
    mmr_after = models.FloatField(null=True)

    final_items = models.JSONField(default=dict)
    gpm = models.FloatField(null=True)

    def mmr_diff(self):
        return self.mmr_after - self.mmr_before

    def get_kda(self):
        if self.hero_kills + self.hero_assists == 0 or self.deaths:
            return 0
        return (self.hero_kills + self.hero_assists) / self.deaths

    def get_kd(self):
        if self.hero_kills == 0 or self.deaths:
            return 0
        return self.hero_kills / self.deaths

    def __str__(self):
        return f"{self.match} {self.account}"
