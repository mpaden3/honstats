# Generated by Django 3.1.5 on 2021-11-20 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0005_auto_20210209_1841"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="fetched_date_custom",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="fetched_date_midwars",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="fetched_date_ranked",
            field=models.DateTimeField(null=True),
        ),
    ]
