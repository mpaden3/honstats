# Generated by Django 3.1.5 on 2021-01-31 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("match", "0008_player_item_times"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match",
            name="parsed_level",
            field=models.TextField(
                choices=[
                    ("1", "Known"),
                    ("2", "Fetched"),
                    ("3", "Replay parsed"),
                    ("4", "Not found"),
                ],
                default="1",
                max_length=1,
            ),
        ),
    ]
