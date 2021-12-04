import datetime
import json

from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from account.models import Account
from game_data.models import Hero, Item
from match import constants
from match.managers import MatchManager


class Match(TimeStampedModel):
    objects = MatchManager()

    MAX_ATTEMPTS = 5
    MAX_TIME = 120

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
    GAME_MODES = [
        (constants.MODE_RANKED, "Ranked"),
        (constants.MODE_CUSTOM, "Custom"),
        (constants.MODE_MIDWARS, "Midwars"),
    ]

    match_id = models.IntegerField(primary_key=True)
    match_date = models.DateTimeField(null=True, db_index=True)
    match_name = models.CharField(max_length=127)
    game_mode = models.TextField(
        max_length=1, choices=GAME_MODES, default=constants.MODE_RANKED
    )
    replay_log_url = models.CharField(max_length=511)
    duration = models.IntegerField(null=True)
    concede = models.BooleanField(default=False)
    winning_team = models.TextField(
        max_length=1, choices=WINNING_TEAM, default=TEAM_EMPTY
    )
    parsed_level = models.TextField(max_length=1, choices=PARSED_LEVELS, default=KNOWN)

    # Parsed data
    networth_diff = models.JSONField(null=True)
    exp_diff = models.JSONField(null=True)
    boss_kills = models.JSONField(null=True)

    attempts = models.IntegerField(default=0)
    last_attempt_time = models.DateTimeField(null=True)

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

    def should_be_parsed(self):

        return self.last_attempt_time is None or (
            self.attempts < Match.MAX_ATTEMPTS
            and self.last_attempt_time + timezone.timedelta(seconds=Match.MAX_TIME)
            < timezone.now()
        )

    def add_attempt(self):
        self.attempts += 1
        self.last_attempt_time = timezone.now()
        self.save()

    def __str__(self):
        if self.match_name:
            return self.match_name
        return str(self.match_id)

    def get_boss_kills_range(self, team):
        kills = 0
        if self.boss_kills:
            kills = self.boss_kills.get(team) or 0
        return range(kills)

    @property
    def get_legion_boss_kills_range(self):
        return self.get_boss_kills_range(Match.TEAM_LEGION)

    @property
    def get_hellbourne_boss_kills_range(self):
        return self.get_boss_kills_range(Match.TEAM_HELLBOURNE)

    def average_mmr(self):
        if self.parsed_level == self.KNOWN:
            return None

        total = 0.0
        players = 0
        for player in self.player_set.all():
            if player.mmr_before:
                total += player.mmr_before
                players += 1
        if players == 0:
            return 0
        return round(total / players)

    def get_kills(self):
        team1_kills = 0
        team2_kills = 0
        for player in self.player_set.all():
            if player.team == "1":
                team1_kills += player.hero_kills
            if player.team == "2":
                team2_kills += player.hero_kills
        return team1_kills, team2_kills

    def losing_team(self):
        if self.winning_team == Match.TEAM_LEGION:
            return Match.TEAM_HELLBOURNE
        if self.winning_team == Match.TEAM_HELLBOURNE:
            return Match.TEAM_LEGION
        return Match.TEAM_EMPTY


class Player(TimeStampedModel):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
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
    obs_wards = models.IntegerField(null=True)
    rev_wards = models.IntegerField(null=True)
    dewards = models.IntegerField(null=True)
    uncountered_wards = models.IntegerField(null=True)
    mmr_before = models.FloatField(null=True)
    mmr_after = models.FloatField(null=True)

    final_items = models.JSONField(default=dict)
    gpm = models.IntegerField(null=True)
    apm = models.IntegerField(null=True)

    # parsed fields

    networth_time = models.JSONField(null=True)
    item_times = models.JSONField(null=True)

    @property
    def ward_success_percent(self):
        if self.obs_wards == 0 and self.rev_wards == 0:
            return 0

        if self.obs_wards is not None and self.uncountered_wards is not None:
            return self.uncountered_wards / (self.obs_wards + self.rev_wards)

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
