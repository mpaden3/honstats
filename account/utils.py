from datetime import datetime

from match.models import Match, Player
from account.models import Account


def update_or_create_account_from_stats(data, create_matches=True):
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

    if create_matches:
        match_dates = parse_match_dates(data["matchDates"])
        match_ids = data["matchIds"].split(" ")
        i = 0
        for match_id in match_ids:
            if match_id != "":
                match_date = datetime.strptime(match_dates[i], "%m/%d/%Y")
                match, created = Match.objects.get_or_create(
                    match_id=int(match_id), match_date=match_date
                )
                if created:
                    match.match_date = match_date
                    match.save()

                    player = Player(account=account, match=match)
                    player.save()
            i += 1

    return account


def parse_match_dates(dates_string):
    n = 10
    return [dates_string[i : i + n] for i in range(0, len(dates_string), n)]
