from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from sicoin.domain_config.models import DomainConfig, IncidentType
from sicoin.domain_config.serializers import DomainFromDatabaseSerializer
from sicoin.incident.models import Incident


class ListIncidentSerializer(serializers.ModelSerializer):
    domain_config = DomainFromDatabaseSerializer()

    class Meta:
        model = Incident
        exclude = []
        depth = 1


class CreateIncidentSerializer(serializers.Serializer):
    domain_name = serializers.CharField(max_length=255)
    incident_type_name = serializers.CharField(max_length=255)
    visibility = serializers.ChoiceField(choices=Incident.INCIDENT_VISIBILITIES)
    details = serializers.JSONField()
    status = serializers.ChoiceField(choices=Incident.INCIDENT_STATUSES)
    data_status = serializers.ChoiceField(choices=Incident.INCIDENT_DATA_STATUSES)
    location_as_string_reference = serializers.CharField(max_length=255, allow_blank=True)
    location_point = GeometryField()

    def validate(self, data):
        try:
            DomainConfig.objects.get(domain_name=data.get('domain_name'))
        except DomainConfig.DoesNotExist:
            raise serializers.ValidationError(f"Domain {data.get('domain_name')} does not exist")

        try:
            IncidentType.objects.get(name=data.get('incident_type_name'))
        except IncidentType.DoesNotExist:
            raise serializers.ValidationError(f"Incident type {data.get('incident_type_name')} does not exist")

        return data

    def create(self, validated_data):
        incident = Incident()
        incident.domain_config = DomainConfig.objects.get(domain_name=validated_data.get('domain_name'))
        incident.incident_type = IncidentType.objects.get(name=validated_data.get('incident_type_name'))
        incident.visibility = validated_data.get('visibility')
        incident.details = validated_data.get('details')
        incident.status = validated_data.get('status')
        incident.data_status = validated_data.get('data_status')
        incident.location_as_string_reference = validated_data.get('location_as_string_reference')
        incident.location_point = validated_data.get('location_point')
        incident.save()
        return incident

    def to_representation(self, instance: Incident):
        location_point = GeometryField().to_representation(instance.location_point)

        return {
            'id': instance.id,
            'domain_name': instance.domain_config.domain_name,
            'incident_type_name': instance.incident_type.name,
            'visibility': instance.visibility,
            'details': instance.details,
            'data_status': instance.data_status,
            'status': instance.status,
            'location_as_string_reference': instance.location_as_string_reference,
            'location_point': location_point,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'finalized_at': instance.finalized_at,
        }

    class Meta:
        fields = ('id', 'domain_name', 'incident_type_name', 'visibility', 'details',
                  'data_status', 'status', 'location_as_string_reference',
                  'location_point', 'created_at', 'updated_at', 'finalized_at')
