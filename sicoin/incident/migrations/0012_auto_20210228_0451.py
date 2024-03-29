# Generated by Django 3.0.8 on 2021-02-28 04:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_resourceprofile_device'),
        ('incident', '0011_auto_20210223_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalincidentresource',
            name='container_resource',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.ResourceProfile'),
        ),
        migrations.AddField(
            model_name='incidentresource',
            name='container_resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='incident_resource_as_container', to='users.ResourceProfile'),
        ),
        migrations.AlterField(
            model_name='incidentresource',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='incident_resource', to='users.ResourceProfile'),
        ),
    ]
