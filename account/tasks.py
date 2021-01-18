import os

import requests
from phpserialize import loads
from honstats.settings import BASE_DIR

from account.utils import update_or_create_account_from_stats


def fetch_player_data(nickname):
    request_data = {
        "f": "show_stats",
        "table": "campaign",
        "nickname": nickname,
    }

    response = requests.post(
        "http://masterserver.naeu.heroesofnewerth.com/client_requester.php",
        request_data,
    ).content
    data = loads(response, decode_strings=True)
    update_or_create_account_from_stats(data)


def fetch_dummy_player_data():
    with open(os.path.join(BASE_DIR, "resources/phparray.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_account_from_stats(data)
