import os

import requests
from phpserialize import loads
from honstats.settings import BASE_DIR

from .utils import create_account_from_stats


def fetch_player_data():
    request_data = {
        "f": "show_stats",
        "table": "campaign",
        "nickname": "yeo",
    }

    with open(os.path.join(BASE_DIR, "resources/phparray.txt"), "r") as file:
        response = file.read().replace("\n", "")

    # response = requests.post('http://masterserver.naeu.heroesofnewerth.com/client_requester.php', request_data)
    data = loads(response.encode(), decode_strings=True)
    account = create_account_from_stats(data)
    account.save()
