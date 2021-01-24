from account.factory import get_or_create_account_from_stats
from match.factory import get_or_create_player_basic
from match.models import Match
from match.utils import update_match_basic


def update_or_create_account_from_stats(data, match_data, create_matches=True):
    account = get_or_create_account_from_stats(data)

    if create_matches:
        for num, match_dat in match_data.items():

            if isinstance(match_dat, dict) and match_dat["map"] == "caldavar":
                match, created = Match.objects.get_or_create(
                    match_id=int(match_dat["match_id"])
                )
                if created or match.parsed_level == Match.KNOWN:
                    update_match_basic(match, match_dat)
                    get_or_create_player_basic(match, account, match_dat)

    return account
