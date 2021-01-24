import os

import requests
from django.http import Http404
from phpserialize import loads

from account.utils import update_or_create_account_from_stats
from honstats.settings import BASE_DIR, CLIENT_REQUESTER_URL


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
