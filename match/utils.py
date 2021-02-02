from datetime import datetime
import pytz
from django.utils import timezone

from account.factory import get_or_create_account_with_id
from match.factory import get_or_create_player_full
from match.models import Match


def update_or_create_match_full(match_id, data):
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        match = Match(
            match_id=match_id,
        )
    match_data = data["match_summ"][match_id]
    date = datetime.strptime(
        match_data["date"] + match_data["time"], "%m/%d/%Y%I:%M:%S %p"
    )  # 05:27:06 AM
    date = pytz.utc.localize(date) + timezone.timedelta(hours=-8)
    match.match_date = date
    match.match_name = match_data["mname"]
    match.duration = int(match_data["time_played"])
    match.winning_team = match_data["winning_team"]
    match.replay_log_url = match_data["s3_url"].replace(".honreplay", ".zip")
    match.parsed_level = Match.FETCHED
    match.save()

    for account_id, player_data in data["match_player_stats"][match_id].items():
        account = get_or_create_account_with_id(account_id, player_data["nickname"], player_data["tag"])
        if account_id not in data["inventory"][match_id]:
            data["inventory"][match_id][account_id] = {}
        get_or_create_player_full(
            match,
            account,
            player_data,
            data["inventory"][match_id][account_id],
            int(match_data["time_played"]),
        )
    return match


def update_match_basic(match, match_dat):
    match.duration = match_dat["secs"]
    date = datetime.strptime(match_dat["mdt"], "%Y-%m-%d %H:%M:%S")
    date = pytz.utc.localize(date)
    match.match_date = date
    if match_dat["wins"] == "1":
        match.winning_team = match_dat["team"]
    else:
        match.winning_team = str(int(match_dat["team"]) % 2 + 1)
    match.save()

    return match


def fix_dates():
    matches = Match.objects.all()

    for match in matches:
        match.match_date = match.match_date + timezone.timedelta(hours=-8)
        match.save()
