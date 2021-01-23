from datetime import datetime

from account.factory import get_or_create_account_from_stats
from match.factory import get_or_create_empty_player
from match.models import Match
from match.utils import parse_match_dates


def update_or_create_account_from_stats(data, create_matches=True):
    account = get_or_create_account_from_stats(data)

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

                player = get_or_create_empty_player(match, account)
                player.save()
            i += 1

    return account
