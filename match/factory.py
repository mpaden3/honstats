from game_data.utils import parse_items, find_hero
from match.models import Player


def create_empty_player(match, account):
    return Player(account=account, match=match)


def get_or_create_player_from_data(match, account, data, inventory):
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
    player.hero_assists = int(data["heroassists"])
    player.networth = int(data["gold"])
    player.hero_damage = int(data["herodmg"])
    player.lasthits = int(data["teamcreepkills"])
    player.denies = int(data["denies"])
    player.wards = int(data["wards"])
    player.mmr_before = float(data["campaign_info"]["mmr_before"])
    player.mmr_after = float(data["campaign_info"]["mmr_after"])

    player.final_items = parse_items(inventory)

    # parse 6 items
    player.save()

    return player


def parse_boolean(string):
    if string == "0":
        return False
    return True
