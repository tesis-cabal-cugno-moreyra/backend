from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from sicoin.geolocation.models import MapPoint, TrackPoint
from sicoin.incident.models import Incident, IncidentResource
from sicoin.users.models import ResourceProfile
from sicoin.users.serializers import ListRetrieveResourceProfileSerializer


class BasePointSerializer(serializers.Serializer):
    def _validate_incident_resource_already_created(self):
        try:
            IncidentResource.objects.get(
                incident_id=self.context.get('incident_id'),
                resource_id=self.context.get('resource_id'))
        except IncidentResource.DoesNotExist:
            raise serializers.ValidationError(
                {'resource_id': f"Resource with id: {self.context.get('resource_id')} is not "
                                f"related to Incident with id:{self.context.get('incident_id')}"})

    def _validate_incident_resource_exists(self):
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


class MapPointSerializer(BasePointSerializer):
    location = GeometryField()
    comment = serializers.CharField(max_length=255)
    time_created = serializers.DateTimeField()
    # resource_id and incident_id could be ignored, as they should be part of the context

    def validate(self, data):
        self._validate_incident_resource_exists()
        self._validate_incident_resource_already_created()
        return data

    def create(self, validated_data):
        map_point = MapPoint()
        map_point.incident_id = self.context.get('incident_id')
        map_point.incident_resource = IncidentResource.objects.get(
            incident_id=self.context.get('incident_id'),
            resource_id=self.context.get('resource_id'))
        map_point.description_text = validated_data.get('comment')
        map_point.location = validated_data.get('location')
        map_point.time_created = validated_data.get('time_created')
        map_point.save()
        return map_point

    def to_representation(self, instance: MapPoint):
        return {
            'location': GeometryField().to_representation(instance.location),
            'collected_at': instance.time_created.isoformat(),
            'internal_type': 'MapPoint',  # We use this field for future usage on WS
            'resource': ListRetrieveResourceProfileSerializer().to_representation(instance.incident_resource.resource),
            'comment': instance.description_text
        }


class TrackPointSerializer(BasePointSerializer):
    location = GeometryField()
    time_created = serializers.DateTimeField()
    # resource_id and incident_id could be ignored, as they should be part of the context

    def validate(self, data):
        self._validate_incident_resource_exists()
        self._validate_incident_resource_already_created()
        return data

    def _check_if_track_point_already_created(self, incident_id, resource_id, time_created):
        track_points = TrackPoint.objects.filter(time_created=time_created, incident_id=incident_id,
                                                 incident_resource_id=resource_id)
        if track_points.count():
            return True
        return False

    def create(self, validated_data):
        # if self._check_if_track_point_already_created(self.context.get('incident_id'), self.context.get('resource_id'),
        #                                               self.context.get('time_created')):
        #     raise Exception("Trackpoint already created!")
        track_point = TrackPoint()
        track_point.incident_id = self.context.get('incident_id')
        track_point.incident_resource = IncidentResource.objects.get(
            incident_id=self.context.get('incident_id'),
            resource_id=self.context.get('resource_id'))
        track_point.location = validated_data.get('location')
        track_point.time_created = validated_data.get('time_created')
        track_point.save()
        return track_point

    def to_representation(self, instance: TrackPoint):
        return {
            'location': GeometryField().to_representation(instance.location),
            'collected_at': instance.time_created.isoformat(),
            'internal_type': 'TrackPoint',  # We use this field for future usage on WS
            'resource': ListRetrieveResourceProfileSerializer().to_representation(instance.incident_resource.resource),
        }


class TrackPointCreateIncidentResourceSerializer(TrackPointSerializer):

    def validate(self, data):
        try:
            Incident.objects.get(id=self.context.get('incident_id'))
        except Incident.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {self.context.get('incident_id')} does not exist"})

        try:
            resource = ResourceProfile.objects.get(id=self.context.get('resource_id'))
        except ResourceProfile.DoesNotExist:
            raise serializers.ValidationError(
                {'resource_id': f"Resource with id: {self.context.get('resource_id')} does not exist"})

        if not resource.user.is_active:
            raise serializers.ValidationError(
                {'resource_id': f"User related to Resource with id: "
                                f"{self.context.get('resource_id')} is not active"})
        return data


class TrackPointListSerializer(BasePointSerializer):
    track_points = TrackPointCreateIncidentResourceSerializer(many=True)

    def validate(self, data):
        return data

    def to_representation(self, instance: TrackPoint):
        return {
            'location': GeometryField().to_representation(instance.location),
            'collected_at': instance.time_created.isoformat(),
            'internal_type': 'TrackPoint',  # We use this field for future usage on WS
            'resource': ListRetrieveResourceProfileSerializer().to_representation(instance.incident_resource.resource),
        }

    def create(self, validated_data):
        track_points = validated_data.pop('track_points', [])
        track_point_instances = []
        for serialized_track_point in track_points:
            track_point = TrackPoint()
            track_point.incident_id = self.context.get('incident_id')
            track_point.incident_resource = IncidentResource.objects.get_or_create(
                incident_id=self.context.get('incident_id'),
                resource_id=self.context.get('resource_id'))[0]
            track_point.location = serialized_track_point.get('location')
            track_point.time_created = serialized_track_point.get('time_created')
            track_point.save()
            track_point_instances.append(track_point)

        return track_point_instances
