from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from sicoin.domain_config.models import DomainConfig, IncidentType
from sicoin.domain_config.serializers import DomainFromDatabaseSerializer
from sicoin.incident.models import Incident
from jsonschema import validate, ValidationError


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
    location_as_string_reference = serializers.CharField(max_length=255, allow_blank=True)
    location_point = GeometryField()

    def validate(self, data):
        try:
            DomainConfig.objects.get(domain_name=data.get('domain_name'))
        except DomainConfig.DoesNotExist:
            raise serializers.ValidationError(
                {'domain_name': f"Domain {data.get('domain_name')} does not exist"})

        try:
            IncidentType.objects.get(name=data.get('incident_type_name'))
        except IncidentType.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_type_name': f"Incident type {data.get('incident_type_name')}"
                                       f"does not exist"})

        return data

    def create(self, validated_data):
        incident = Incident()
        incident.domain_config = DomainConfig.objects.get(domain_name=validated_data.get('domain_name'))
        incident.incident_type = IncidentType.objects.get(name=validated_data.get('incident_type_name'))
        incident.visibility = validated_data.get('visibility')
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
            'data_status': instance.data_status,
            'status': instance.status,
            'location_as_string_reference': instance.location_as_string_reference,
            'location_point': location_point,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'finalized_at': instance.finalized_at,
        }

    class Meta:
        fields = ('id', 'domain_name', 'incident_type_name', 'visibility',
                  'data_status', 'status', 'location_as_string_reference',
                  'location_point', 'created_at', 'updated_at', 'finalized_at')


class ValidateIncidentDetailsSerializer(serializers.Serializer):
    incident_id = serializers.IntegerField()
    details = serializers.JSONField()

    def validate(self, data):
        try:
            incident = Incident.objects.get(id=data.get('incident_id'))
        except Incident.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {data.get('incident_id')} does not exist"})

        details_schema = incident.incident_type.details_schema
        details_data = data.get('details')
        try:
            validate(instance=details_data, schema=details_schema)
        except ValidationError as error:
            raise serializers.ValidationError(
                {'details': f"Details validation failed. Error: {error}"})
        return data

    def create(self, validated_data):
        incident = Incident.objects.get(id=validated_data.get('incident_id'))
        incident.details = validated_data.get('details')
        incident.data_status = Incident.INCIDENT_DATA_STATUS_COMPLETE
        incident.save()
        return incident

    class Meta:
        fields = ('incident_id', 'details')
