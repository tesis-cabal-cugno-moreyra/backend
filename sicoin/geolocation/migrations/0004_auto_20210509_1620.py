# Generated by Django 3.0.14 on 2021-05-09 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geolocation', '0003_auto_20201121_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mappoint',
            name='time_created',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='trackpoint',
            name='time_created',
            field=models.DateTimeField(),
        ),
    ]
