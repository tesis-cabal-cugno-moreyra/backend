from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from sicoin.incident.models import Incident, IncidentResource


class BasePointInTime(models.Model):
    location = models.PointField(default=Point(0.0, 0.0))
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TrackPoint(BasePointInTime):
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT)
    incident_resource = models.ForeignKey(IncidentResource, on_delete=models.PROTECT)


class MapPoint(BasePointInTime):
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT)
    incident_resource = models.ForeignKey(IncidentResource, on_delete=models.PROTECT)
    description_text = models.TextField()
