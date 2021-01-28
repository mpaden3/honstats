from django import template

register = template.Library()


@register.filter
def humanize_bool(bool_val: bool):
    if bool_val:
        return "Yes"
    return "No"
