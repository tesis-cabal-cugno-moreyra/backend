# Generated by Django 3.0.8 on 2020-11-21 00:41

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('geolocation', '0002_auto_20201012_0301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mappoint',
            name='point_in_time',
        ),
        migrations.RemoveField(
            model_name='trackpoint',
            name='point_in_time',
        ),
        migrations.AddField(
            model_name='mappoint',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), srid=4326),
        ),
        migrations.AddField(
            model_name='mappoint',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trackpoint',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(0.0, 0.0), srid=4326),
        ),
        migrations.AddField(
            model_name='trackpoint',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PointInTime',
        ),
    ]
