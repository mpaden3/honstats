def find_hero(hero_id):
    return None  # TODO


def parse_items(inventory):
    items = {}

    if "slot_1" in inventory:
        items["slot_1"] = inventory["slot_1"]
    else:
        items["slot_1"] = None

    if "slot_2" in inventory:
        items["slot_2"] = inventory["slot_2"]
    else:
        items["slot_2"] = None

    if "slot_3" in inventory:
        items["slot_3"] = inventory["slot_3"]
    else:
        items["slot_3"] = None

    if "slot_4" in inventory:
        items["slot_4"] = inventory["slot_4"]
    else:
        items["slot_4"] = None

    if "slot_5" in inventory:
        items["slot_5"] = inventory["slot_5"]
    else:
        items["slot_5"] = None

    if "slot_6" in inventory:
        items["slot_6"] = inventory["slot_6"]
    else:
        items["slot_6"] = None

    return items
