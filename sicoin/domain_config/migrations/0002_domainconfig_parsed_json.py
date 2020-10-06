# Generated by Django 3.0.8 on 2020-09-19 06:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain_config', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainconfig',
            name='parsed_json',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]