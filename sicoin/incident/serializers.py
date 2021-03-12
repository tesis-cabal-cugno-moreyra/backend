from rest_framework import serializers, status
from rest_framework_gis.fields import GeometryField

from sicoin.domain_config.models import DomainConfig, IncidentType
from sicoin.domain_config.serializers import DomainFromDatabaseSerializer
from sicoin.incident.models import Incident, IncidentResource, IncidentResourceContainerMustBeAbleToContainResources, \
    IncidentResourceForContainersCannotHaveAContainerRelatedException
from jsonschema import validate, ValidationError

from sicoin.users.models import ResourceProfile
from sicoin.users.serializers import ListRetrieveResourceProfileSerializer


class ListIncidentSerializer(serializers.ModelSerializer):
    domain_config = DomainFromDatabaseSerializer()

    class Meta:
        model = Incident
        exclude = []
        depth = 1


class CreateIncidentSerializer(serializers.Serializer):
    domain_name = serializers.CharField(max_length=255)
    incident_type_name = serializers.CharField(max_length=255)
    external_assistance = serializers.ChoiceField(choices=Incident.INCIDENT_ASSISTANCE_OPTIONS)
    location_as_string_reference = serializers.CharField(max_length=255, allow_blank=True)
    reference = serializers.CharField(max_length=255)
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
        incident.external_assistance = validated_data.get('external_assistance')
        incident.location_as_string_reference = validated_data.get('location_as_string_reference')
        incident.location_point = validated_data.get('location_point')
        incident.reference = validated_data.get('reference')
        incident.save()
        return incident

    def to_representation(self, instance: Incident):
        location_point = GeometryField().to_representation(instance.location_point)

        return {
            'id': instance.id,
            'domain_name': instance.domain_config.domain_name,
            'incident_type_name': instance.incident_type.name,
            'external_assistance': instance.external_assistance,
            'data_status': instance.data_status,
            'status': instance.status,
            'location_as_string_reference': instance.location_as_string_reference,
            'location_point': location_point,
            'reference': instance.reference,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'cancelled_at': instance.cancelled_at,
            'finalized_at': instance.finalized_at,
        }

    class Meta:
        fields = ('id', 'domain_name', 'incident_type_name', 'external_assistance',
                  'reference', 'data_status', 'status', 'location_as_string_reference',
                  'location_point', 'created_at', 'updated_at', 'finalized_at')


class ValidateIncidentDetailsSerializer(serializers.Serializer):
    details = serializers.JSONField()

    def validate(self, data):
        try:
            incident = Incident.objects.get(id=self.context.get('incident_id'))
        except Incident.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {self.context.get('incident_id')} does not exist"})

        details_schema = incident.incident_type.details_schema
        details_data = data.get('details')
        try:
            validate(instance=details_data, schema=details_schema)
        except ValidationError as error:
            raise serializers.ValidationError(
                {'details': f"Details validation failed. Error: {error}"})
        return data

    def create(self, validated_data):
        incident = Incident.objects.get(id=self.context.get('incident_id'))
        incident.details = validated_data.get('details')
        incident.data_status = Incident.INCIDENT_DATA_STATUS_COMPLETE
        incident.save()
        return incident

    class Meta:
        fields = ('incident_id', 'details')


class IncidentResourceSerializer(serializers.ModelSerializer):
    incident = CreateIncidentSerializer()
    resource = ListRetrieveResourceProfileSerializer()
    container_resource = ListRetrieveResourceProfileSerializer()

    class Meta:
        model = IncidentResource
        fields = '__all__'


class CreateUpdateIncidentResourceSerializer(serializers.Serializer):
    container_resource_id = serializers.IntegerField(required=False)

    def _get_incident_resource_validated(self, incident_id, resource_id):
        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            raise serializers.ValidationError(
                {'incident_id': f"Incident with id: {incident_id} does not exist"},
                code=status.HTTP_404_NOT_FOUND
            )

        if incident.status != incident.INCIDENT_STATUS_STARTED:
            raise serializers.ValidationError({'incident_id': 'Incident is not at Created state'},
                                              code=status.HTTP_400_BAD_REQUEST)

        try:
            resource = ResourceProfile.objects.get(id=resource_id)
        except ResourceProfile.DoesNotExist:
            raise serializers.ValidationError({'resource_id': 'Resource not found'}, code=status.HTTP_404_NOT_FOUND)

        if not resource.user.is_active:
            raise serializers.ValidationError({'resource_id': 'User resource is not active'},
                                              code=status.HTTP_400_BAD_REQUEST)

    def validate(self, attrs):
        # Validate needed data, to raise exceptions on validation time, previous to save() being called
        self._get_incident_resource_validated(self.context['incident_id'], self.context['resource_id'])

        container_resource_id = attrs['container_resource_id']
        if container_resource_id:
            try:
                ResourceProfile.objects.get(id=container_resource_id)
            except ResourceProfile.DoesNotExist:
                raise serializers.ValidationError({'container_resource_id': 'Container resource not found'},
                                                  code=status.HTTP_404_NOT_FOUND)
        return container_resource_id

    def _add_container_resource_if_retrieved(self, incident_resource: IncidentResource) -> IncidentResource:
        if self.validated_data['container_resource_id']:
            try:
                incident_resource.container_resource = ResourceProfile.objects.get(
                    id=self.validated_data['container_resource_id']
                )
            except ResourceProfile.DoesNotExist:
                raise serializers.ValidationError({'container_resource_id': 'Container resource not found'},
                                                  code=status.HTTP_404_NOT_FOUND)
            # Instead of checking out for the resource corresponding to the vehicle, we generate
            # the IncidentResource here. CHECK THIS!!
            IncidentResource.objects.get_or_create(incident_id=self.validated_data['incident_id'],
                                                   resource_id=self.validated_data['container_resource_id'])

        return incident_resource

    def _reset_incident_resource_if_rejoining(self, incident_resource: IncidentResource) -> IncidentResource:
        existent_incident_resources = IncidentResource.objects.filter(self.validated_data['incident_id'],
                                                                      self.validated_data['resource_id'])
        if len(existent_incident_resources):
            assert incident_resource.id == existent_incident_resources.all()[0]
            if incident_resource.exited_from_incident_at is not None:  # CHECK THIS
                incident_resource.exited_from_incident_at = None
            else:
                raise serializers.ValidationError({'resource_id': 'User resource already joined to this Incident'},
                                                  code=status.HTTP_400_BAD_REQUEST)
        return incident_resource

    def save(self, **kwargs):
        incident_resource = self._get_incident_resource_validated(self.validated_data['incident_id'],
                                                                  self.validated_data['resource_id'])

        incident_resource = self._add_container_resource_if_retrieved(incident_resource)
        incident_resource = self._reset_incident_resource_if_rejoining(incident_resource)

        try:
            incident_resource.save()
        except IncidentResourceForContainersCannotHaveAContainerRelatedException:
            raise serializers.ValidationError({'non_field_error': 'Resource of type Container cannot have a related '
                                                                  'instance of container resource!'},
                                              code=status.HTTP_400_BAD_REQUEST)
        except IncidentResourceContainerMustBeAbleToContainResources:
            raise serializers.ValidationError({'container_resource_id': 'Container resource must be able to contain '
                                                                        'resources'},
                                              code=status.HTTP_400_BAD_REQUEST)

        return incident_resource
