from datetime import datetime

from account.factory import get_or_create_account_with_id
from match.factory import get_or_create_player_from_data
from match.models import Match


def update_or_create_match_from_stats(match_id, data):
    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        match = Match(
            match_id=match_id,
        )
    match_data = data["match_summ"][match_id]
    match.match_date = datetime.strptime(match_data["date"]+match_data["time"], "%m/%d/%Y%I:%M:%S %p") # 05:27:06 AM
    match.match_name = match_data["mname"]
    match.duration = int(match_data["time_played"])
    match.winning_team = match_data["winning_team"]
    match.replay_log_url = match_data["s3_url"].replace(".honreplay", ".zip")
    match.parsed_level = Match.FETCHED
    match.save()

    for account_id, player_data in data["match_player_stats"][match_id].items():
        account = get_or_create_account_with_id(account_id, player_data["nickname"])
        if account_id not in data["inventory"][match_id]:
            data["inventory"][match_id][account_id] = {}
        get_or_create_player_from_data(
            match, account, player_data, data["inventory"][match_id][account_id]
        )
    return match


def parse_match_dates(dates_string):
    date_length = 10
    return [
        dates_string[i : i + date_length]
        for i in range(0, len(dates_string), date_length)
    ]
