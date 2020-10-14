from django.contrib.gis.db import models

from sicoin.incident.models import Incident, IncidentResource


class PointInTime(models.Model):
    location = models.PointField()
    time_created = models.DateTimeField(auto_now_add=True)


class TrackPoint(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT)
    incident_resource = models.ForeignKey(IncidentResource, on_delete=models.PROTECT)
    point_in_time = models.ForeignKey(PointInTime, on_delete=models.PROTECT)


class MapPoint(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT)
    incident_resource = models.ForeignKey(IncidentResource, on_delete=models.PROTECT)
    description_text = models.TextField()
    point_in_time = models.ForeignKey(PointInTime, on_delete=models.PROTECT)
