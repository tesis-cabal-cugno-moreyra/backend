# Generated by Django 3.0.8 on 2021-02-08 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0009_auto_20201115_0432'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalincidentresource',
            name='exited_from_incident_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incidentresource',
            name='exited_from_incident_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
