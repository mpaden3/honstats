from django.db import models

# Create your models here.
from match.models import Match


class ParsedData:
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    parsed_date = models.DateTimeField(null=True)
    # TODO write data
