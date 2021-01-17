from django.db import models


# Create your models here.
class Player(models.Model):
    nickname = models.CharField(max_length=128)
    super_id = models.IntegerField()
    account_id = models.IntegerField()
    games_played = models.IntegerField()
    total_games_played = models.IntegerField()
    last_name = models.CharField(max_length=30)
    create_date = models.DateField()
    last_activity = models.DateField()


class Match(models.Model):
    match_id = models.IntegerField()
    match_date = models.DateField()
    last_name = models.CharField(max_length=30)
    players = models.ForeignKey(Player, on_delete=models.CASCADE)


class Hero(models.Model):
    hero_id = models.IntegerField()
    hero_name = models.CharField(max_length=128)
