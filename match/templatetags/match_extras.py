from django import template

register = template.Library()


@register.filter
def humanize_bool(bool_val: bool):
    if bool_val:
        return "Yes"
    return "No"


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
        return pad(hrs) + ':' + pad(mins) + ':' + pad(secs)
    return pad(mins) + ':' + pad(secs)


def pad(n):
    return ('00' + str(round(n)))[-2:]


@register.filter
def hero_icon(hero_id):
    return f"/img/hero/{hero_id}.jpg"


@register.filter
def item_icon(item_code):
    return f"/img/item/{item_code}.jpg"
