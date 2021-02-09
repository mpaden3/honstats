import re


def parse_nickname_tag(name: str):
    nickname = name
    tag_name = None

    tag = re.search("^\[.*?\]", name)
    if tag:
        nickname = name.replace(tag.group(), '')
        tag_name = tag.group().replace('[', '').replace(']', '')
    return nickname, tag_name
