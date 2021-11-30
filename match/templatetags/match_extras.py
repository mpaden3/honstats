from django import template

from match.models import Match

register = template.Library()


@register.filter
def match_state_verbose(parsed_level):
    if parsed_level == Match.KNOWN:
        return "Match Found"
    if parsed_level == Match.FETCHED:
        return "Basic Data"
    if parsed_level == Match.REPLAY:
        return "Replay Parsed"
    if parsed_level == Match.NOT_FOUND:
        return "Replay could not be found."


@register.filter
def player_color(position):
    if position == "0":
        return "#003ce9"
    if position == "1":
        return "#7cfff1"
    if position == "2":
        return "#613294"
    if position == "3":
        return "#fffc01"
    if position == "4":
        return "#fe8a0e"
    if position == "5":
        return "#e55bb0"
    if position == "6":
        return "#959697"
    if position == "7":
        return "#6aabff"
    if position == "8":
        return "#106246"
    if position == "9":
        return "#ad5c33"


@register.filter
def msec_print(s):
    ms = s % 1000
    s = (s - ms) / 1000
    secs = s % 60
    s = (s - secs) / 60
    mins = s % 60
    hrs = (s - mins) / 60

    if hrs > 0:
        return pad(hrs) + ":" + pad(mins) + ":" + pad(secs)
    return pad(mins) + ":" + pad(secs)


def pad(n):
    return ("00" + str(round(n)))[-2:]


@register.filter
def hero_icon(hero_id):
    return f"img/hero/{hero_id}.jpg"


@register.filter
def item_icon(item_code):
    return f"img/item/{item_code}.jpg"


@register.filter
def show_wards(player):
    if player.obs_wards is not None and player.rev_wards is not None:
        return f'<span class="span-assists">{player.obs_wards}</span>/<span class="account-link">{player.rev_wards}</span>'
    return player.wards


@register.filter
def percentage(value):
    if value is None:
        return format(0, ".0%")
    return format(value, ".0%")


@register.filter
def match_results(args):
    team1_kills = args[0]
    team2_kills = args[1]
    return f"{team1_kills} : {team2_kills}"


@register.filter
def team_verbose(team):
    if team == Match.TEAM_LEGION:
        return "<span class='legion'>Legion</span>"
    return "<span class='hellbourne'>Hellbourne</span>"
