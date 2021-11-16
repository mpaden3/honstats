import random
import time

from account.models import Account
from hon_api.tasks import show_stats, match_history_overview
from match.constants import MODE_RANKED, MODE_CUSTOM, MODE_MIDWARS
from match.factory import get_or_create_player_basic
from match.models import Match
from match.tasks import fetch_match_data


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
            if first and match.is_known():
                fetch_match_data(match.match_id)
                first = False


def fetch_player_data(nickname):
    data = show_stats(nickname)
    account = Account.objects.get_or_create_account_from_stats(data)

    # get ranked match data
    match_data_ranked = match_history_overview(nickname, "campaign")
    # match_data_custom = match_history_overview(nickname, "player")
    # match_data_midwars = match_history_overview(nickname, "other")

    save_matches(match_data_ranked.values(), MODE_RANKED, account)
    # save_matches(match_data_custom.values(), MODE_CUSTOM, account)
    # save_matches(match_data_midwars.values(), MODE_MIDWARS, account)
    account.update_current_mmr()
    account.save()

    return account


def fix_mmr():
    accounts = Account.objects.all()

    for account in accounts:
        if account.current_mmr is None:
            fetch_player_data(account.nickname)
            print(f"Fetched {account.nickname}")
            r = random.randint(1, 10)
            time.sleep(r)
