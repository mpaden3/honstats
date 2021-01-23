import os

import requests
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
    if "account_id" in data:
        return update_or_create_account_from_stats(data)
    return None


def fetch_dummy_player_data():
    with open(os.path.join(BASE_DIR, "resources/phparray.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_account_from_stats(data)
