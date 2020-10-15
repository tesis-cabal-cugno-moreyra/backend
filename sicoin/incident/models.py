from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.gis.db.models import PointField

from sicoin.domain_config.models import DomainConfig, IncidentType
from sicoin.users.models import ResourceProfile, SupervisorProfile


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Incident(BaseModel):
    INCIDENT_STATUS_STARTED = "Started"
    INCIDENT_STATUS_CANCELED = "Canceled"
    INCIDENT_STATUS_FINALIZED = "Finalized"
    INCIDENT_STATUSES = (
        (INCIDENT_STATUS_STARTED, INCIDENT_STATUS_STARTED),
        (INCIDENT_STATUS_CANCELED, INCIDENT_STATUS_CANCELED),
        (INCIDENT_STATUS_FINALIZED, INCIDENT_STATUS_FINALIZED),
    )

    INCIDENT_DATA_STATUS_INCOMPLETE = 'Incomplete'
    INCIDENT_DATA_STATUS_COMPLETE = 'Complete'
    INCIDENT_DATA_STATUSES = (
        (INCIDENT_DATA_STATUS_INCOMPLETE, INCIDENT_DATA_STATUS_INCOMPLETE),
        (INCIDENT_DATA_STATUS_COMPLETE, INCIDENT_DATA_STATUS_COMPLETE)
    )

    INCIDENT_VISIBILITY_PRIVATE = "Private"
    INCIDENT_VISIBILITY_PUBLIC = "Public"
    INCIDENT_VISIBILITIES = (
        (INCIDENT_VISIBILITY_PRIVATE, INCIDENT_VISIBILITY_PRIVATE),
        (INCIDENT_VISIBILITY_PUBLIC, INCIDENT_VISIBILITY_PUBLIC),
    )

    domain_config = models.ForeignKey(DomainConfig, on_delete=models.PROTECT)
    incident_type = models.ForeignKey(IncidentType, on_delete=models.PROTECT)
    visibility = models.CharField(max_length=255,
                                  choices=INCIDENT_VISIBILITIES,
                                  default=INCIDENT_VISIBILITY_PRIVATE)
    details = models.TextField()
    status = models.CharField(max_length=255, choices=INCIDENT_STATUSES,
                              default=INCIDENT_STATUS_STARTED)
    data_status = models.CharField(max_length=255, choices=INCIDENT_DATA_STATUSES,
                                   default=INCIDENT_DATA_STATUS_INCOMPLETE)
    location_as_string_reference = models.CharField(max_length=255, blank=True)
    location_point = PointField()
    finalized_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Incident ({self.id}): type: {self.incident_type.name}, " \
               f"created: {self.created_at}, " \
               f"domain: {self.domain_config.domain_name}"


class IncidentResource(BaseModel):
    incident = models.ForeignKey("Incident", on_delete=models.PROTECT)
    resource = models.ForeignKey(ResourceProfile, on_delete=models.PROTECT)

    def __str__(self):
        return f"Incident Resource ({self.id})"


class IncidentSupervisor(BaseModel):
    incident = models.ForeignKey("Incident", on_delete=models.PROTECT)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.PROTECT)
    # FEATURE: A supervisor could be marked as the "supervisor at charge"
    # It might be needed to validate only one supervisor at charge
    on_charge = models.BooleanField(default=False)

    def __str__(self):
        return f"Incident Supervisor ({self.id})"
