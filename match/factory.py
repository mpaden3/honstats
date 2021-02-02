from account.models import Account
from game_data.utils import parse_items, find_hero
from match.models import Player, Match


def get_or_create_player_basic(match, account, match_dat):
    try:
        player = Player.objects.get(account=account, match=match)
    except Player.DoesNotExist:
        player = Player(account=account, match=match)
    player.team = match_dat["team"]
    player.hero_kills = match_dat["herokills"]
    player.deaths = match_dat["deaths"]
    player.hero_assists = match_dat["heroassists"]
    player.hero = find_hero(int(match_dat["hero_id"]))
    player.save()
    return player


def get_or_create_player_full(
    match: Match, account: Account, data, inventory, time_played: int
):
    try:
        player = Player.objects.get(account=account, match=match)
    except Player.DoesNotExist:
        player = Player(account=account, match=match)

    player.team = data["team"]
    player.position = data["position"]
    player.level = int(data["level"])
    player.hero = find_hero(int(data["hero_id"]))
    player.hero_kills = int(data["herokills"])
    player.deaths = int(data["deaths"])
    player.kicked = parse_boolean(data["kicked"])
    player.disconnect = parse_boolean(data["discos"])
    player.hero_assists = int(data["heroassists"])
    player.networth = int(data["gold"])
    player.hero_damage = int(data["herodmg"])
    player.tower_damage = int(data["bdmg"])
    player.lasthits = int(data["teamcreepkills"]) + int(data["neutralcreepkills"])
    player.denies = int(data["denies"])
    player.wards = int(data["wards"])
    player.mmr_before = float(data["campaign_info"]["mmr_before"])
    player.mmr_after = float(data["campaign_info"]["mmr_after"])
    player.gpm = round(int(data["gold"]) / (time_played / 60.0))
    player.apm = round(int(data["actions"]) / (time_played / 60.0))

    player.final_items = parse_items(inventory)

    player.save()

    return player


def parse_boolean(string):
    if string == "0":
        return False
    return True
