import re

from account.models import Account


def parse_nickname_tag(name: str):
    nickname = name
    tag_name = None

    tag = re.search("^\[.*?\]", name)
    if tag:
        nickname = name.replace(tag.group(), '')
        tag_name = tag.group().replace('[', '').replace(']', '')
    return nickname, tag_name


def fix_tags():
    accounts = Account.objects.all()

    for account in accounts:
        nickname, tag = parse_nickname_tag(account.nickname)
        account.nickname = nickname
        if tag != '':
            account.clan_tag = tag
        account.save()
