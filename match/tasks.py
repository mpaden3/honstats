import os

import requests
from phpserialize import loads

from match.utils import update_or_create_match_from_stats
from honstats.settings import BASE_DIR, HON_COOKIE, CLIENT_REQUESTER_URL


def fetch_match_data(match_id):
    request_data = {
        "f": "get_match_stats",
        "match_id": match_id,
        "cookie": HON_COOKIE,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    data = loads(response, decode_strings=True)
    update_or_create_match_from_stats(match_id, data)


def fetch_dummy_match_data():
    match_id = 160701828
    with open(os.path.join(BASE_DIR, "resources/match.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_match_from_stats(match_id, data)
