from account.models import Account
from hon_api.tasks import show_stats
from match.constants import MODE_RANKED
from match.factory import get_or_create_player_basic
from match.models import Match
from match.tasks import fetch_match_data


def fetch_account_data(nickname):
    data = show_stats(nickname)

    return Account.objects.get_or_create_account_from_stats(data)


def save_matches(matches, game_mode, account):
    first = True
    for match_dat in matches:
        if isinstance(match_dat, dict):
            match, created = Match.objects.get_or_create(
                match_id=int(match_dat["match_id"])
            )
            if created or match.is_known():
                Match.objects.update_match_basic(match, match_dat, game_mode)
                get_or_create_player_basic(match, account, match_dat)
            if first and match.is_known() and game_mode == MODE_RANKED:
                fetch_match_data(match.match_id)
                first = False
