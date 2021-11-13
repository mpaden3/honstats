from django.db import models
from django_extensions.db.models import TimeStampedModel

from account.managers import AccountManager
from match.constants import MODE_RANKED


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
        player = self.matches.filter(match__game_mode=MODE_RANKED).order_by("-match__match_date").first()
        self.current_mmr = round(player.mmr_after)

    def get_season_winrate(self):
        if self.season_wins and self.season_games_played:
            return round((self.season_wins / self.season_games_played) * 100, 2)
