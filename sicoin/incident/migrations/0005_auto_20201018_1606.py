# Generated by Django 3.0.8 on 2020-10-18 16:06

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0004_auto_20201015_0016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalincident',
            name='details',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='incident',
            name='details',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]