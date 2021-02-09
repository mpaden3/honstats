from account.models import Account
from account.utils import parse_nickname_tag
from hon_api.tasks import show_stats, match_history_overview
from match.factory import get_or_create_player_basic
from match.models import Match
from match.tasks import fetch_match_data


def fetch_player_data(nickname):
    data = show_stats(nickname)
    account = Account.objects.get_or_create_account_from_stats(data)

    # get match data
    match_data = match_history_overview(nickname)
    first = True
    for _, match_dat in match_data.items():
        if isinstance(match_dat, dict) and match_dat["map"] == "caldavar":
            match, created = Match.objects.get_or_create(
                match_id=int(match_dat["match_id"])
            )
            if created or match.is_known():
                Match.objects.update_match_basic(match, match_dat)
                get_or_create_player_basic(match, account, match_dat)
            if first and match.is_known():
                fetch_match_data(match.match_id)
            first = False
    account.update_current_mmr()
    account.save()

    return account


def fix_tags():
    accounts = Account.objects.all()

    for account in accounts:
        nickname, tag = parse_nickname_tag(account.nickname)
        account.nickname = nickname
        if tag != '':
            account.clan_tag = tag
        account.save()
