import datetime
import json

from django.db import models
from django_extensions.db.models import TimeStampedModel
from account.models import Account
from game_data.models import Hero, Item
from match.managers import MatchManager


class Match(TimeStampedModel):

    objects = MatchManager()

    TEAM_EMPTY = "0"
    TEAM_LEGION = "1"
    TEAM_HELLBOURNE = "2"

    KNOWN = "1"
    FETCHED = "2"
    REPLAY = "3"
    NOT_FOUND = "4"
    PARSED_LEVELS = [
        (KNOWN, "Known"),
        (FETCHED, "Fetched"),
        (REPLAY, "Replay parsed"),
        (NOT_FOUND, "Not found"),
    ]
    WINNING_TEAM = [
        (TEAM_EMPTY, "Empty"),
        (TEAM_LEGION, "Legion"),
        (TEAM_HELLBOURNE, "Hellbourne"),
    ]

    match_id = models.IntegerField(primary_key=True)
    match_date = models.DateTimeField(null=True, db_index=True)
    match_name = models.CharField(max_length=127)
    replay_log_url = models.CharField(max_length=511)
    duration = models.IntegerField(null=True)
    winning_team = models.TextField(
        max_length=1, choices=WINNING_TEAM, default=TEAM_EMPTY
    )
    parsed_level = models.TextField(max_length=1, choices=PARSED_LEVELS, default=KNOWN)

    # Parsed data
    networth_diff = models.JSONField(null=True)
    exp_diff = models.JSONField(null=True)

    class Meta:
        ordering = ["-match_id"]

    def duration_format(self):
        if self.duration is None:
            return ""

        return str(datetime.timedelta(seconds=self.duration))

    def is_known(self):
        return self.parsed_level == self.KNOWN

    def is_fetched(self):
        return self.parsed_level == self.FETCHED

    def is_parsed(self):
        return self.parsed_level == self.REPLAY

    def __str__(self):
        if self.match_name:
            return self.match_name
        return str(self.match_id)

    def average_mmr(self):
        if self.parsed_level == self.KNOWN:
            return None

        total = 0.0
        players = 0
        for player in self.player_set.all():
            if player.mmr_before:
                total += player.mmr_before
                players += 1
        return round(total / players)


class Player(TimeStampedModel):
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    account = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, related_name="matches"
    )
    TEAM = [
        (Match.TEAM_EMPTY, "Empty"),
        (Match.TEAM_LEGION, "Legion"),
        (Match.TEAM_HELLBOURNE, "Hellbourne"),
    ]
    team = models.TextField(max_length=1, choices=TEAM, default=Match.TEAM_EMPTY)
    position = models.TextField(max_length=1, null=True)
    level = models.IntegerField(null=True)
    hero = models.ForeignKey(Hero, on_delete=models.DO_NOTHING, null=True)
    hero_kills = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    kicked = models.BooleanField(default=False)
    disconnect = models.BooleanField(default=False)
    hero_assists = models.IntegerField(null=True)
    networth = models.IntegerField(null=True)
    hero_damage = models.IntegerField(null=True)
    tower_damage = models.IntegerField(null=True)
    lasthits = models.IntegerField(null=True)
    denies = models.IntegerField(null=True)
    wards = models.IntegerField(null=True)
    mmr_before = models.FloatField(null=True)
    mmr_after = models.FloatField(null=True)

    final_items = models.JSONField(default=dict)
    gpm = models.IntegerField(null=True)
    apm = models.IntegerField(null=True)

    # parsed fields

    networth_time = models.JSONField(null=True)
    item_times = models.JSONField(null=True)

    def get_item_times(self):
        return json.loads(self.item_times)

    def is_winner(self):
        return self.match.winning_team == self.team

    def mmr_diff(self):
        if self.mmr_after and self.mmr_before:
            return round(self.mmr_after - self.mmr_before, 2)
        return None

    def get_kda(self):
        if self.hero_kills + self.hero_assists == 0 or self.deaths == 0:
            return 0
        return (self.hero_kills + self.hero_assists) / self.deaths

    def get_kd(self):
        if self.hero_kills == 0 or self.deaths == 0:
            return 0
        return round(self.hero_kills / self.deaths, 2)

    def __str__(self):
        return f"{self.match} {self.account}"

    def get_items(self):
        items = []
        for slot, item in self.final_items.items():
            try:
                if item is None:
                    items.append(Item(code="Backpack", name="Empty"))
                item = Item.objects.get(code=item)
                items.append(item)
            except Item.DoesNotExist:
                continue
        return items
