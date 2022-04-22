from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin
from sicoin.incident import models


@admin.register(models.Incident)
class IncidentAdmin(LeafletGeoAdmin):
    list_display = ("id", "incident_type", "status", "data_status", "location_point", "reference")


@admin.register(models.IncidentResource)
class IncidentResourceAdmin(LeafletGeoAdmin):
    list_display = ("id", "incident", "resource", "container_resource")
