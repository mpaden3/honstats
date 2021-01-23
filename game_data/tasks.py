import os

from game_data.factory import create_item
from honstats.settings import BASE_DIR


def import_items():
    path = os.path.join(BASE_DIR, "resources/item")
    file_set = []

    for root, dirs, files in os.walk(path):
        for file in files:
            file_set.append(file.split(".")[0])
    for file_name in file_set:
        create_item(file_name)
