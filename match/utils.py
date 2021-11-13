from datetime import datetime
import pytz
from django.utils import timezone

from account.models import Account
from match.factory import get_or_create_player_full
from match.models import Match
from match.constants import MODE_RANKED, MODE_CUSTOM, MODE_MIDWARS


def determine_game_mode(game_mode_data):
    if game_mode_data == 'cp':
        return MODE_RANKED
    if game_mode_data == 'cm':
        return MODE_CUSTOM

    return None

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
    match.game_mode = determine_game_mode(match_data['gamemode'])
    match.duration = int(match_data["time_played"])
    match.winning_team = match_data["winning_team"]
    match.replay_log_url = match_data["s3_url"].replace(".honreplay", ".zip")
    match.parsed_level = Match.FETCHED
    match.save()

    for account_id, player_data in data["match_player_stats"][match_id].items():
        account = Account.objects.get_or_create_account_with_id(
            account_id, player_data["nickname"], player_data["tag"]
        )
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
