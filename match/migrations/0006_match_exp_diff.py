# Generated by Django 3.1.5 on 2021-01-29 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0005_match_networth_diff'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='exp_diff',
            field=models.JSONField(null=True),
        ),
    ]