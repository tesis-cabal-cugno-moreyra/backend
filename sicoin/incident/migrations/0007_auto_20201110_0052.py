# Generated by Django 3.0.8 on 2020-11-10 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incident', '0006_auto_20201025_2109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalincident',
            name='visibility',
        ),
        migrations.RemoveField(
            model_name='incident',
            name='visibility',
        ),
        migrations.AddField(
            model_name='historicalincident',
            name='external_assistance',
            field=models.CharField(choices=[('With external support', 'With external support'), ('Without external support', 'Without external support')], default='Without external support', max_length=255),
        ),
        migrations.AddField(
            model_name='incident',
            name='external_assistance',
            field=models.CharField(choices=[('With external support', 'With external support'), ('Without external support', 'Without external support')], default='Without external support', max_length=255),
        ),
    ]
