import os

import requests
from django.http import Http404
from phpserialize import loads

from account.factory import get_or_create_account_from_stats
from honstats.settings import BASE_DIR, CLIENT_REQUESTER_URL
from match.factory import get_or_create_player_basic
from match.models import Match
from match.utils import update_match_basic


def fetch_player_data(nickname):
    request_data = {
        "f": "show_stats",
        "table": "campaign",
        "nickname": nickname,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    data = loads(response, decode_strings=True)
    if "account_id" not in data:
        raise Http404

    request_data = {
        "f": "match_history_overview",
        "table": "campaign",
        "nickname": nickname,
        "num": 100,
        "current_season": 1,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    match_data = loads(response, decode_strings=True)

    return update_or_create_account_from_stats(data, match_data)


def fetch_dummy_player_data():
    with open(os.path.join(BASE_DIR, "resources/phparray.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_account_from_stats(data)


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
