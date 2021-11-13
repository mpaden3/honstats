import subprocess
from phpserialize import loads

import requests
from django.http import Http404

from hon_api.models import ApiKey
from honstats.settings import CLIENT_REQUESTER_URL


def api_login():
    api_key = ApiKey.objects.all().first()
    username = api_key.username
    password = api_key.password
    result = subprocess.run(
        [f"./refresh_api_login.sh { username} {password}"], stdout=subprocess.PIPE, shell=True
    )

    cookie = result.stdout.decode().replace("\n", "")
    api_key.cookie = cookie
    api_key.save()

    return cookie


def grab_last_matches_from_nick(nickname):
    request_data = {
        "f": "grab_last_matches_from_nick",
        "nickname": nickname,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    data = loads(response, decode_strings=True)
    if "last_stats" not in data:
        raise Http404
    return data


def show_stats(nickname):
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
    return data


def match_history_overview(nickname, num_of_matches=100, current_season=1):
    request_data = {
        "f": "match_history_overview",
        "table": "campaign",
        "nickname": nickname,
        "num": num_of_matches,
        "current_season": current_season,
    }

    response = requests.post(
        CLIENT_REQUESTER_URL,
        request_data,
    ).content
    return loads(response, decode_strings=True)


def get_match_stats(match_id):
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
