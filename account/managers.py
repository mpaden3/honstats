from datetime import datetime

import pytz
from django.db import models
from django.utils import timezone

from account.utils import parse_nickname_tag


class AccountManager(models.Manager):
    def get_or_create_account_from_stats(self, data):

        account, _ = self.get_or_create(account_id=data["account_id"])
        account.super_id = data["super_id"]

        if date := data["create_date"]:
            account.create_date = pytz.utc.localize(datetime.strptime(date, "%m/%d/%Y"))
        if date := data["last_activity"]:
            account.last_activity = pytz.utc.localize(
                datetime.strptime(date, "%m/%d/%Y")
            )

        nickname, tag = parse_nickname_tag(data["nickname"])
        account.nickname = nickname
        account.clan_tag = tag
        account.games_played = int(data.get("games_played") or 0)
        account.total_games_played = int(data.get("total_games_played") or 0)
        account.season_games_played = int(data.get("curr_season_cam_games_played") or 0)
        account.season_wins = int(data.get("cam_wins") or 0)
        account.season_losses = int(data.get("cam_losses") or 0)
        account.fetched_date = timezone.now()
        account.save()
        return account

    def get_or_create_account_with_id(self, account_id, nickname, tag):
        account, created = self.get_or_create(account_id=account_id)

        if created:
            account.nickname = nickname
            if tag != "":
                account.clan_tag = tag
            account.save()
        return account
