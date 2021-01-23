from django.db import models


class Hero(models.Model):
    hero_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, null=True)
    code = models.CharField(max_length=128, unique=True, null=True)

    def image_html(self):
        return f'<img src="/static/img/hero/{self.hero_id}.jpg" class="item-icon" title="{self.name}" />'


class Item(models.Model):
    name = models.CharField(max_length=128, null=True)
    code = models.CharField(max_length=255, db_index=True, unique=True)

    def image_html(self):
        return f'<img src="/static/img/item/{self.code}.jpg" class="item-icon" title="{self.name}" />'
