from datetime import datetime
import pytz
from django.utils import timezone

from account.models import Account
from match.factory import get_or_create_player_full
from match.models import Match
import match.constants


# game modes
# cp
# ap All Pick, Custom Game
# cm Captains Mode, Custom game
# ss
# hb Hero ban, Midwars
# ar All Random, Midwars or Custom Game

def determine_game_mode(game_mode, game_map):
    if game_map == "midwars":
        return match.constants.MODE_MIDWARS
    if game_map == "devowars":
        return match.constants.MODE_CUSTOM
    if game_map == "caldavar" and game_mode == "cp":
        return match.constants.MODE_RANKED
    if game_mode == "cm" or game_mode == "ap" or game_mode == "ss":
        return match.constants.MODE_CUSTOM
    if game_mode == "hb":
        return match.constants.MODE_MIDWARS

    return None


def determine_game_mode_table(game_mode):
    if game_mode == match.constants.MODE_RANKED:
        return "campaign"
    if game_mode == match.constants.MODE_MIDWARS:
        return "other"
    if game_mode == match.constants.MODE_CUSTOM:
        return "player"
    return None


def update_or_create_match_full(match_id, data):
    match, _ = Match.objects.get_or_create(match_id=match_id)
    match_data = data["match_summ"][match_id]
    date = datetime.strptime(
        match_data["date"] + match_data["time"], "%m/%d/%Y%I:%M:%S %p"
    )  # 05:27:06 AM
    date = pytz.utc.localize(date) + timezone.timedelta(hours=-8)
    match.match_date = date
    match.match_name = match_data["mname"]
    match.game_mode = determine_game_mode(match_data.get("gamemode"), match_data["map"])
    match.duration = int(match_data["time_played"])
    match.winning_team = match_data["winning_team"]
    if match_data["s3_url"]:
        match.replay_log_url = match_data["s3_url"].replace(".honreplay", ".zip")
    match.parsed_level = Match.FETCHED
    match.save()

    for account_id, player_data in data["match_player_stats"][match_id].items():
        account = Account.objects.get_or_create_account_with_id(
            account_id, player_data["nickname"], player_data["tag"]
        )
        if "inventory" not in data or account_id not in data["inventory"][match_id]:
            inventory = {}
        else:
            inventory = data["inventory"][match_id][account_id]
        get_or_create_player_full(
            match,
            account,
            player_data,
            inventory,
            int(match_data["time_played"]),
        )
    return match
