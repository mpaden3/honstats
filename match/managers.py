from datetime import datetime

import pytz
from django.db import models
from django.utils import timezone


class MatchManager(models.Manager):
    def update_match_basic(self, match, match_dat, game_mode):
        match.duration = match_dat["secs"]
        date = datetime.strptime(match_dat["mdt"], "%Y-%m-%d %H:%M:%S")
        date = pytz.utc.localize(date) + timezone.timedelta(hours=-8)
        match.match_date = date
        match.game_mode = game_mode
        if match_dat["wins"] == "1":
            match.winning_team = match_dat["team"]
        else:
            match.winning_team = str(int(match_dat["team"]) % 2 + 1)
        match.save()

        return match
