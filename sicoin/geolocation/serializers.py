from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from sicoin.geolocation.models import MapPoint
from sicoin.incident.models import Incident, IncidentResource
from sicoin.users.models import ResourceProfile


class MapPointSerializer(serializers.Serializer):
    location = GeometryField()
    comment = serializers.CharField(max_length=255)
    # resource_id and incident_id could be ignored, as they should be part of the endpoint

    def validate(self, data):
        try:
            incident = Incident.objects.get(id=self.context.get('incident_id'))
        except Incident.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {self.context.get('incident_id')} does not exist"})

        if incident.status != incident.INCIDENT_STATUS_STARTED:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {self.context.get('incident_id')} "
                                f"is not at Created state"})

        try:
            resource = ResourceProfile.objects.get(id=self.context.get('resource_id'))
        except ResourceProfile.DoesNotExist:
            raise serializers.ValidationError(
                {'resource_id': f"Resource with id: {self.context.get('resource_id')} does not exist"})

        if not resource.user.is_active:
            raise serializers.ValidationError(
                {'resource_id': f"User related to Resource with id: "
                                f"{self.context.get('resource_id')} is not active"})

        try:
            IncidentResource.objects.get(
                incident_id=self.context.get('incident_id'),
                resource_id=self.context.get('resource_id'))
        except IncidentResource.DoesNotExist:
            raise serializers.ValidationError(
                {'resource_id': f"Resource with id: {self.context.get('resource_id')} is not "
                                f"related to Incident with id:{self.context.get('incident_id')}"})

        return data

    def create(self, validated_data):
        map_point = MapPoint()
        map_point.incident_id = self.context.get('incident_id')
        map_point.incident_resource = IncidentResource.objects.get(
            incident_id=self.context.get('incident_id'),
            resource_id=self.context.get('resource_id'))
        map_point.description_text = validated_data.get('comment')
        map_point.location = validated_data.get('location')
        map_point.save()
        return map_point

    def to_representation(self, instance: MapPoint):
        return {
            'location': GeometryField().to_representation(instance.location),
            'collected_at': instance.time_created,
            'internal_type': 'MapPoint',  # We use this field for future usage on WS
            'resource_id': instance.incident_resource.resource_id,
            'comment': instance.description_text
        }
