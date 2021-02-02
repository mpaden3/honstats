from datetime import datetime

import pytz
from django.utils import timezone
from account.models import Account
from account.utils import parse_nickname_tag


def get_or_create_account_from_stats(data):
    try:
        account = Account.objects.get(account_id=data["account_id"])
    except Account.DoesNotExist:
        account = Account(
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
    account.fetched_date = timezone.now()
    account.save()
    return account


def get_or_create_account_with_id(account_id, nickname, tag):
    try:
        account = Account.objects.get(account_id=account_id)
    except Account.DoesNotExist:
        account = Account(account_id=account_id)
        account.nickname = nickname
        if tag != '':
            account.clan_tag = tag
        account.save()
    return account
