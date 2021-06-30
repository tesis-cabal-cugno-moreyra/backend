from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from encrypted_fields import fields


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SupervisorAlias(BaseModel):
    alias = models.CharField(max_length=255)
    domain_config = models.ForeignKey('DomainConfig', on_delete=models.PROTECT)

    def __str__(self):
        return f"SupervisorAlias ({self.id}): alias: {self.alias}, domain: {self.domain_config.domain_name}"

    class Meta:
        verbose_name_plural = "Supervisor Aliases"
        constraints = [
            models.UniqueConstraint(fields=['domain_config', 'alias'],
                                    name='unique supervisor alias for a domain')
        ]


class ResourceType(BaseModel):
    name = models.CharField(max_length=255)
    is_able_to_contain_resources = models.BooleanField(default=False)
    domain_config = models.ForeignKey('DomainConfig', on_delete=models.PROTECT)

    def __str__(self):
        return f"ResourceType ({self.id}): name: {self.name}, domain: {self.domain_config.domain_name}, " \
               f"contains resources: {self.is_able_to_contain_resources}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['domain_config', 'name'],
                                    name='unique resource name for a domain')
        ]


class MapPointDescription(BaseModel):
    text = models.TextField()
    incident_type = models.ForeignKey('IncidentType', on_delete=models.PROTECT)

    @property
    def domain_config(self):
        return self.incident_type.domain_config

    def __str__(self):
        return f"MapPointDescriptions ({self.id}): incident type: {self.incident_type.name}"


class IncidentTypeResource(BaseModel):
    incident_type = models.ForeignKey('IncidentType', on_delete=models.PROTECT)
    resource_type = models.ForeignKey('ResourceType', on_delete=models.PROTECT)

    @property
    def domain_config(self):
        # FIXME: This is not necessarily true, as same domain_config should be validated
        return self.resource_type.domain_config

    def __str__(self):
        return f"IncidentTypeResources ({self.id}): incident type: {self.incident_type.name}, " \
               f"resource: {self.resource_type.name}"


class IncidentType(BaseModel):
    name = models.CharField(max_length=255)
    abstraction = models.ForeignKey('IncidentAbstraction', on_delete=models.PROTECT)
    details_schema = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    general_stats = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)

    @property
    def domain_config(self):
        return self.abstraction.domain_config

    def __str__(self):
        return f"IncidentType ({self.id}): name: {self.name}, abstraction: {self.abstraction.alias}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'abstraction'],
                                    name='unique incident type name for related abstraction')
        ]


class IncidentAbstraction(BaseModel):
    alias = models.CharField(max_length=255)
    domain_config = models.ForeignKey('DomainConfig', on_delete=models.PROTECT)

    def __str__(self):
        return f"IncidentAbstraction ({self.id}): alias: {self.alias}, " \
               f"domain: {self.domain_config.domain_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['domain_config', 'alias'],
                                    name='unique incident abstraction alias for domain_config')
        ]


class DomainConfig(BaseModel):
    domain_name = models.CharField(max_length=255, unique=True)
    admin_alias = models.CharField(max_length=255)
    domain_code = fields.EncryptedCharField(help_text="Code used for domain-related tasks", max_length=255)
    parsed_json = JSONField()

    @property
    def domain_config(self):
        return self

    def __str__(self):
        return f"DomainConfig ({self.id}): name: {self.domain_name}"
