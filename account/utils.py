from datetime import datetime

from match.models import Match
from .models import Account


def create_account_from_stats(data, create_matches=True):
    account = Account(
        super_id=data["super_id"],
        nickname=data["nickname"],
        account_id=data["account_id"],
        games_played=int(data["games_played"]),
        total_games_played=int(data["total_games_played"]),
        create_date=datetime.strptime(data["create_date"], "%m/%d/%Y"),
        last_activity=datetime.strptime(data["last_activity"], "%m/%d/%Y"),
    )

    if create_matches:
        match_ids = data["matchIds"].split(" ")
        for match_id in match_ids:
            match = Match.objects.get_or_create(match_id=int(match_id))
            match.save()

    return account
