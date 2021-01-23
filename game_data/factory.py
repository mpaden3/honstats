from game_data.models import Item


def create_item(code):
    item = Item(code=code)
    item.save()
    return item
