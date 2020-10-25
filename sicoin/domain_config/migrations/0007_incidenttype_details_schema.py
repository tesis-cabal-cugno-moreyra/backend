# Generated by Django 3.0.8 on 2020-10-22 00:44

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain_config', '0006_auto_20201012_0127'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidenttype',
            name='details_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]