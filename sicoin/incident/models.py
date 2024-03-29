from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.gis.db.models import PointField

from sicoin.domain_config.models import DomainConfig, IncidentType
from sicoin.users.models import ResourceProfile, SupervisorProfile


class IncidentResourceForContainersCannotHaveAContainerRelatedException(BaseException):
    pass


class IncidentResourceContainerMustBeAbleToContainResources(BaseException):
    pass


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class StartedIncidentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Incident.INCIDENT_STATUS_STARTED)


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

    INCIDENT_ASSISTANCE_WITH_EXTERNAL_SUPPORT = "With external support"
    INCIDENT_ASSISTANCE_WITHOUT_EXTERNAL_SUPPORT = "Without external support"
    INCIDENT_ASSISTANCE_OPTIONS = (
        (INCIDENT_ASSISTANCE_WITH_EXTERNAL_SUPPORT, INCIDENT_ASSISTANCE_WITH_EXTERNAL_SUPPORT),
        (INCIDENT_ASSISTANCE_WITHOUT_EXTERNAL_SUPPORT, INCIDENT_ASSISTANCE_WITHOUT_EXTERNAL_SUPPORT),
    )

    domain_config = models.ForeignKey(DomainConfig, on_delete=models.PROTECT)
    incident_type = models.ForeignKey(IncidentType, on_delete=models.PROTECT)
    external_assistance = models.CharField(max_length=255,
                                           choices=INCIDENT_ASSISTANCE_OPTIONS,
                                           default=INCIDENT_ASSISTANCE_WITHOUT_EXTERNAL_SUPPORT)
    details = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    status = models.CharField(max_length=255, choices=INCIDENT_STATUSES,
                              default=INCIDENT_STATUS_STARTED)
    data_status = models.CharField(max_length=255, choices=INCIDENT_DATA_STATUSES,
                                   default=INCIDENT_DATA_STATUS_INCOMPLETE)
    location_as_string_reference = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    location_point = PointField()
    finalized_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    @property
    def status_is_started(self):
        return self.status == self.INCIDENT_STATUS_STARTED

    @property
    def status_is_cancelled(self):
        return self.status == self.INCIDENT_STATUS_CANCELED

    @property
    def status_is_finalized(self):
        return self.status == self.INCIDENT_STATUS_FINALIZED

    objects = models.Manager()  # FIXME: Refactor to incidents or all_incidents
    started_incidents = StartedIncidentManager()

    def __str__(self):
        return f"Incident ({self.id}): type: {self.incident_type.name}, " \
               f"created: {self.created_at}, " \
               f"domain: {self.domain_config.domain_name}"


class IncidentResource(BaseModel):
    incident = models.ForeignKey("Incident", on_delete=models.PROTECT)
    resource = models.ForeignKey(ResourceProfile, related_name="incident_resource", on_delete=models.PROTECT)
    container_resource = models.ForeignKey(ResourceProfile, related_name="incident_resource_as_container",
                                           on_delete=models.PROTECT, blank=True, null=True)
    exited_from_incident_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Incident Resource ({self.id})"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.resource.type.is_able_to_contain_resources and self.container_resource:
            raise IncidentResourceForContainersCannotHaveAContainerRelatedException()

        if self.container_resource and not self.container_resource.type.is_able_to_contain_resources:
            raise IncidentResourceContainerMustBeAbleToContainResources()

        # CHECK FOR OTHER FAILURE CONDITIONS

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['incident', 'resource'], name="Unique incident resource relation")
        ]


class IncidentSupervisor(BaseModel):
    incident = models.ForeignKey("Incident", on_delete=models.PROTECT)
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.PROTECT)
    # FEATURE: A supervisor could be marked as the "supervisor at charge"
    # It might be needed to validate only one supervisor at charge
    on_charge = models.BooleanField(default=False)

    def __str__(self):
        return f"Incident Supervisor ({self.id})"
