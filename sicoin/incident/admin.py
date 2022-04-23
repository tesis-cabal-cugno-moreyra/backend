from django.contrib.gis import admin
from sicoin.incident import models


@admin.register(models.Incident)
class IncidentAdmin(admin.OSMGeoAdmin):
    list_display = ("id", "incident_type", "status", "data_status", "location_point", "reference")


@admin.register(models.IncidentResource)
class IncidentResourceAdmin(admin.OSMGeoAdmin):
    list_display = ("id", "incident", "resource", "container_resource")
