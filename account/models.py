from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel

from account.managers import AccountManager
from honstats.settings import REQUEST_TIMEOUT
from match.constants import MODE_RANKED, MODE_MIDWARS, MODE_CUSTOM


class Account(TimeStampedModel):
    objects = AccountManager()

    account_id = models.IntegerField(primary_key=True)
    nickname = models.CharField(max_length=256, null=True, db_index=True)
    clan_tag = models.CharField(max_length=128, null=True, db_index=True)
    super_id = models.IntegerField(null=True)
    games_played = models.IntegerField(null=True)
    total_games_played = models.IntegerField(null=True)
    create_date = models.DateField(null=True)
    last_activity = models.DateField(null=True)
    fetched_date = models.DateTimeField(null=True)
    fetched_date_ranked = models.DateTimeField(null=True)
    fetched_date_custom = models.DateTimeField(null=True)
    fetched_date_midwars = models.DateTimeField(null=True)
    current_mmr = models.IntegerField(null=True)
    season_games_played = models.IntegerField(null=True)
    season_wins = models.IntegerField(null=True)
    season_losses = models.IntegerField(null=True)

    class Meta:
        ordering = ["nickname"]

    def __str__(self):
        return self.get_player_name()

    def get_player_name(self):
        if self.clan_tag:
            return f"[{self.clan_tag}]{self.nickname}"
        return self.nickname

    def update_current_mmr(self):
        if player := self.matches.filter(match__game_mode=MODE_RANKED).order_by("-match__match_date").first():
            self.current_mmr = round(player.mmr_after)

    def get_season_winrate(self):
        if self.season_wins and self.season_games_played:
            return round((self.season_wins / self.season_games_played) * 100, 2)

    def should_be_updated(self):
        return self.fetched_date is None or self.fetched_date + timezone.timedelta(
            seconds=REQUEST_TIMEOUT) < timezone.now()

    def should_fetch_matches(self, game_mode):
        field = None
        if game_mode == MODE_RANKED:
            field = self.fetched_date_ranked
        if game_mode == MODE_MIDWARS:
            field = self.fetched_date_midwars
        if game_mode == MODE_CUSTOM:
            field = self.fetched_date_custom

        return field is None or field + timezone.timedelta(
            seconds=REQUEST_TIMEOUT) < timezone.now()

    def update_fetch_time(self, game_mode):
        if game_mode == MODE_RANKED:
            self.fetched_date_ranked = timezone.now()
        if game_mode == MODE_MIDWARS:
            self.fetched_date_midwars = timezone.now()
        if game_mode == MODE_CUSTOM:
            self.fetched_date_custom = timezone.now()
        self.save()
