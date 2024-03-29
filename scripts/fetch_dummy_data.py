import os

from django.utils import timezone
from phpserialize import loads

from match.models import Match
from match.utils import update_or_create_match_full
from honstats.settings import BASE_DIR


def fetch_dummy_match_data():
    match_id = 160701828
    with open(os.path.join(BASE_DIR, "resources/match.txt"), "r") as file:
        response = file.read().replace("\n", "")

    data = loads(response.encode(), decode_strings=True)
    update_or_create_match_full(match_id, data)


def fix_dates():
    matches = Match.objects.all()

    for match in matches:
        match.match_date = match.match_date + timezone.timedelta(hours=-8)
        match.save()
