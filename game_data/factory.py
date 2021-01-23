from game_data.models import Item, Hero


def create_item(code):
    item = Item(code=code)
    item.save()
    return item


def create_hero(hero_id):
    hero = Hero(hero_id=hero_id)
    hero.save()
    return Hero
