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
