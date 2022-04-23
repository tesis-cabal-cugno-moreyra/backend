from django.contrib.gis import admin
from sicoin.geolocation import models


@admin.register(models.TrackPoint)
class TrackPointAdmin(admin.OSMGeoAdmin):
    list_display = ("id", "incident", "incident_resource", "location", "time_created")


@admin.register(models.MapPoint)
class MapPointAdmin(admin.OSMGeoAdmin):
    list_display = ("id", "incident", "incident_resource", "location", "time_created", "description_text")
