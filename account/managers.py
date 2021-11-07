from datetime import datetime

import pytz
from django.db import models
from django.utils import timezone
from django.apps import apps

from account.utils import parse_nickname_tag


class AccountManager(models.Manager):
    def get_or_create_account_from_stats(self, data):

        model = self._get_model()

        try:
            account = self.get(account_id=data["account_id"])
        except model.DoesNotExist:
            account = model(
                account_id=data["account_id"],
            )
        account.super_id = data["super_id"]
        date = datetime.strptime(data["create_date"], "%m/%d/%Y")
        date = pytz.utc.localize(date)
        account.create_date = date

        date = datetime.strptime(data["last_activity"], "%m/%d/%Y")
        date = pytz.utc.localize(date)
        account.last_activity = date

        nickname, tag = parse_nickname_tag(data["nickname"])
        account.nickname = nickname
        account.clan_tag = tag
        account.last_activity = datetime.strptime(data["last_activity"], "%m/%d/%Y")
        account.games_played = int(data["games_played"])
        account.total_games_played = int(data["total_games_played"])
        account.season_games_played = int(data["curr_season_cam_games_played"])
        account.season_wins = int(data["cam_wins"])
        account.season_losses = int(data["cam_losses"])
        account.fetched_date = timezone.now()
        account.save()
        return account

    def get_or_create_account_with_id(self, account_id, nickname, tag):

        model = self._get_model()

        try:
            account = self.get(account_id=account_id)
        except model.DoesNotExist:
            account = model(account_id=account_id)
            account.nickname = nickname
            if tag != "":
                account.clan_tag = tag
            account.save()
        return account

    def _get_model(self):
        return apps.get_model(app_label="account", model_name="Account")
