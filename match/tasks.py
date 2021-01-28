import os

import requests
from django.http import Http404
from phpserialize import loads

from hon_api.models import ApiKey
from hon_api.tasks import api_login
from match.utils import update_or_create_match_full
from honstats.settings import BASE_DIR, CLIENT_REQUESTER_URL


def send_request(match_id):
    request_data = {
        "f": "get_match_stats",
        "match_id": match_id,
        "cookie": ApiKey.objects.all().first().cookie,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    data = loads(response, decode_strings=True)

    if "match_summ" not in data:
        cookie = api_login()

        request_data = {
            "f": "get_match_stats",
            "match_id": match_id,
            "cookie": cookie,
        }

        response = requests.post(
            CLIENT_REQUESTER_URL,
            request_data,
        ).content
        data = loads(response, decode_strings=True)

    return data


def fetch_match_data(match_id):
    data = send_request(match_id)

    if (
        "date" not in data["match_summ"][match_id]
        or data["match_summ"][match_id]["map"] != "caldavar"
    ):
        raise Http404

    return update_or_create_match_full(match_id, data)


def fetch_dummy_match_data():
    match_id = 160701828
    with open(os.path.join(BASE_DIR, "resources/match.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_match_full(match_id, data)
