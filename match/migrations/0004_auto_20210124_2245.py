# Generated by Django 3.1.5 on 2021-01-24 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("match", "0003_auto_20210123_2051"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="apm",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="player",
            name="disconnect",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="player",
            name="gpm",
            field=models.IntegerField(null=True),
        ),
    ]