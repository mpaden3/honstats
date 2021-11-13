import io
import os
from io import BytesIO

import requests
import zipfile

from django.http import Http404

from honstats.settings import BASE_DIR
from log_parser.log_actions import MatchData, parse_log_entry
from match.exceptions import ReplayNotFoundException
from match.models import Match


def parse_match_data(match_id: int):
    match = Match.objects.get(match_id=match_id)
    if not match.is_fetched():
        return match
    url = match.replay_log_url
    zip_file = requests.get(url, allow_redirects=True)
    if zip_file.status_code != 200:
        raise ReplayNotFoundException

    lines = []
    with zipfile.ZipFile(BytesIO(zip_file.content), "r") as zfile:
        for name in zfile.namelist():
            with zfile.open(name) as readfile:
                for line in io.TextIOWrapper(readfile, "utf-16"):
                    lines.append(line.replace("\n", ""))

    match_data = MatchData()

    for line in lines:
        try:
            action = parse_log_entry(line)
        except UnicodeDecodeError:
            continue
        if action:
            action.apply(match_data)

    match_data.dump_data(match)
    match.parsed_level = Match.REPLAY
    match.save()
    return match


def parse_dummy_match_data():
    with open(
        os.path.join(BASE_DIR, "resources/m162495279.log"), encoding="utf-16"
    ) as f:
        lines = f.readlines()

    match_data = MatchData()

    for line in lines:
        action = parse_log_entry(line)
        if action:
            action.apply(match_data)
    networth_diff = {}

    for i in range(0, match_data.end_time, 100000):
        networth_diff[i] = match_data.get_networth_diff(i)
    networth_diff[match_data.end_time] = match_data.get_networth_diff(
        match_data.end_time
    )
    print(networth_diff)
