# Generated by Django 3.1.5 on 2021-11-30 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("match", "0016_match_concede"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="boss_kills",
            field=models.JSONField(null=True),
        ),
    ]