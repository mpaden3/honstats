from django.db import models
from django_extensions.db.models import TimeStampedModel


class Account(TimeStampedModel):
    account_id = models.IntegerField(primary_key=True)
    nickname = models.CharField(max_length=128, null=True, db_index=True)
    clan_tag = models.CharField(max_length=128, null=True, db_index=True)
    super_id = models.IntegerField(null=True)
    games_played = models.IntegerField(null=True)
    total_games_played = models.IntegerField(null=True)
    create_date = models.DateField(null=True)
    last_activity = models.DateField(null=True)
    fetched_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ["nickname"]

    def __str__(self):
        if self.clan_tag:
            return f"[{self.clan_tag}]{self.nickname}"

        return self.nickname

    def get_player_name(self):
        if self.clan_tag:
            return f"[{self.clan_tag}]{self.nickname}"
        return self.nickname
