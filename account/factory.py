from datetime import datetime

from account.models import Account


def get_or_create_account_from_stats(data):
    try:
        account = Account.objects.get(account_id=data["account_id"])
    except Account.DoesNotExist:
        account = Account(
            super_id=data["super_id"],
            account_id=data["account_id"],
            create_date=datetime.strptime(data["create_date"], "%m/%d/%Y"),
            last_activity=datetime.strptime(data["last_activity"], "%m/%d/%Y"),
        )
    account.nickname = data["nickname"]
    account.last_activity = datetime.strptime(data["last_activity"], "%m/%d/%Y")
    account.games_played = int(data["games_played"])
    account.total_games_played = int(data["total_games_played"])
    account.save()
    return account


def get_or_create_account_with_id(account_id, nickname):
    try:
        account = Account.objects.get(account_id=account_id)
    except Account.DoesNotExist:
        account = Account(account_id=account_id)
        account.nickname = nickname
    account.save()
    return account