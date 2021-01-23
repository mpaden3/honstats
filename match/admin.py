from django.contrib import admin

# Register your models here.
from match.models import Player, Match

admin.site.register(Match)
admin.site.register(Player)
