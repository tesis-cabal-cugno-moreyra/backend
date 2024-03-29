from rest_framework import serializers
from rest_framework.fields import JSONField

from sicoin.domain_config import models
from sicoin.domain_config.models import DomainConfig, ResourceType
from sicoin.domain_config.utils import get_random_alphanumeric_string


class DomainSerializer(serializers.Serializer):

    def create_instance(self, validated_data, domain):
        raise Exception("Method not implemented")


class ResourceTypeSerializer(DomainSerializer):
    name = serializers.CharField(max_length=200)
    isAbleToContainResources = serializers.BooleanField(default=False)


class SupervisorAliasSerializer(DomainSerializer):
    name = serializers.CharField(max_length=200)

    def create_instance(self, validated_data, domain):
        for supervisor_alias in validated_data:
            models.SupervisorAlias.objects.create(**{
                'alias': supervisor_alias.get('name'),
                'domain_config': domain
            })


class MapPointDescriptionSerializer(DomainSerializer):
    text = serializers.CharField(max_length=200)


class IncidentTypeSerializer(DomainSerializer):
    name = serializers.CharField(max_length=200)
    descriptions = MapPointDescriptionSerializer(many=True)
    detailsSchema = JSONField()
    resourceTypes = ResourceTypeSerializer(many=True)


class IncidentAbstractionSerializer(DomainSerializer):
    name = serializers.CharField(max_length=200)
    types = IncidentTypeSerializer(many=True)

    def create_instance(self, validated_data, domain):
        for incident_abstraction in validated_data:
            incident_abstraction_instance = models.IncidentAbstraction.objects.create(**{
                'alias': incident_abstraction.get('name'),
                'domain_config': domain
            })
            for incident_type in incident_abstraction.get('types'):
                incident_type_instance = models.IncidentType.objects.create(**{
                    'name': incident_type.get('name'),
                    'details_schema': incident_type.get('detailsSchema'),
                    'abstraction': incident_abstraction_instance
                })
                for description in incident_type.get('descriptions'):
                    models.MapPointDescription.objects.create(**{
                        'text': description.get('text'),
                        'incident_type': incident_type_instance
                    })
                for resource_type in incident_type.get('resourceTypes'):
                    resource_instance = models.ResourceType.objects.update_or_create(**{
                        'name': resource_type.get('name'),
                        'is_able_to_contain_resources': resource_type.get('isAbleToContainResources'),
                        'domain_config': domain
                    })
                    models.IncidentTypeResource.objects.update_or_create(**{
                        'incident_type': incident_type_instance,
                        'resource_type': resource_instance[0]
                    })


class DomainSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    supervisorAliases = SupervisorAliasSerializer(many=True)
    adminAlias = serializers.CharField(max_length=200)
    incidentAbstractions = IncidentAbstractionSerializer(many=True)
    resourceTypes = ResourceTypeSerializer(many=True)

    def create(self, validated_data):
        domain_code = get_random_alphanumeric_string(10)

        domain_data = {
            'domain_name': validated_data.get('name'),
            'admin_alias': validated_data.get('adminAlias'),
            'parsed_json': validated_data,
            'domain_code': domain_code
        }
        domain = models.DomainConfig.objects.create(**domain_data)

        SupervisorAliasSerializer().create_instance(validated_data.get('supervisorAliases'), domain)

        IncidentAbstractionSerializer().create_instance(validated_data.get('incidentAbstractions'), domain)

        return domain

    def update(self, instance, validated_data):
        raise Exception("Not implemented function")


class DomainFromDatabaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DomainConfig
        exclude = ['parsed_json', 'domain_code']


class ResourceTypeFromDatabaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceType
        exclude = []


class CheckDomainCodeSerializer(serializers.Serializer):
    domain_code = serializers.CharField(max_length=200)

    def validate_domain_code(self, value):
        try:
            domain = DomainConfig.objects.all()[0]
        except IndexError:
            raise serializers.ValidationError("Incorrect code or No Domain exists")

        if domain.domain_code != value:
            raise serializers.ValidationError("Incorrect code or No Domain exists")
        return value
