import json
from datetime import datetime

import django_filters
from django.http import HttpResponse
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, mixins, viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from sicoin.incident import models, serializers
from sicoin.incident.consumers import AvailableIncidentTypes
from sicoin.incident.models import Incident, IncidentResource
from sicoin.incident.serializers import IncidentResourceSerializer
from sicoin.users.models import ResourceProfile
from sicoin.users.notify_user_manager import IncidentCreationNotificationManager


class IncidentCreateListViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = Incident.objects.all()
    serializer_class = serializers.CreateIncidentSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'incident_type__name': ['exact'],
        'external_assistance': ['exact'],
        'status': ['exact'],
        'data_status': ['exact'],
        'reference': ['icontains'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListIncidentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ListIncidentSerializer(queryset, many=True)
        return Response(serializer.data)


class ChangeIncidentExternalAssistanceAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Set incident external assistance as With or Without "
                                               "external support, Only Admin user",
                         responses={200: "{'message': 'Changed incident status successfully'}",
                                    400: "{'message': 'Incident with id {ID} does not exists'},"
                                         "{'message': 'Incident external assistance as --- already set'}"})
    def post(self, request, incident_id):
        if not incident_id:
            return HttpResponse(json.dumps({'message': 'Incident id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Incident with id {incident_id} '
                                                       f'does not exists'}),
                                status=status.HTTP_400_BAD_REQUEST)

        if incident.external_assistance == self.get_incident_external_assistance_change_to():
            return HttpResponse(json.dumps({'message': f'Incident external assistance as '
                                                       f'{self.get_incident_external_assistance_change_to()} '
                                                       f'already set'}),
                                status=status.HTTP_400_BAD_REQUEST)

        incident.external_assistance = self.get_incident_external_assistance_change_to()
        incident.save()
        return HttpResponse(json.dumps({'message': 'Changed incident assistance successfully'}))

    def get_incident_external_assistance_change_to(self) -> str:
        raise NotImplementedError()


class IncidentAssistanceWithExternalSupportAPIView(ChangeIncidentExternalAssistanceAPIView):
    def get_incident_external_assistance_change_to(self) -> str:
        return Incident.INCIDENT_ASSISTANCE_WITH_EXTERNAL_SUPPORT


class IncidentAssistanceWithoutExternalSupportAPIView(ChangeIncidentExternalAssistanceAPIView):
    def get_incident_external_assistance_change_to(self) -> str:
        return Incident.INCIDENT_ASSISTANCE_WITHOUT_EXTERNAL_SUPPORT


class ChangeIncidentStatusAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Change incident status to Cancelled or Finalized",
                         responses={200: "{'message': 'Changed incident status successfully'}",
                                    400: "{'message': 'Incident with id {ID} does not exists'},"
                                         "{'message': 'Incident status as --- already set'}"})
    def post(self, request, incident_id):
        if not incident_id:
            return HttpResponse(json.dumps({'message': 'Incident id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Incident with id {incident_id} '
                                                       f'does not exists'}),
                                status=status.HTTP_400_BAD_REQUEST)

        if self.is_able_to_change_status(incident):
            incident.status = self.get_incident_status_change_to()
            incident = self.make_changes_to_incident_according_to_status_change(incident)
            incident.save()
            return HttpResponse(json.dumps({'message': 'Changed incident status successfully'}))
        else:
            return HttpResponse(json.dumps({'message': f'Incident with id {incident_id} '
                                                       f'cannot change from state {incident.status} to '
                                                       f'state {self.get_incident_status_change_to()}'}),
                                status=status.HTTP_400_BAD_REQUEST)

    def get_incident_status_change_to(self) -> str:
        raise NotImplementedError()

    def is_able_to_change_status(self, incident: Incident) -> bool:
        raise NotImplementedError()

    def make_changes_to_incident_according_to_status_change(self, incident: Incident) -> Incident:
        raise NotImplementedError()


class IncidentStatusFinalizeAPIView(ChangeIncidentStatusAPIView):
    def get_incident_status_change_to(self) -> str:
        return Incident.INCIDENT_STATUS_FINALIZED

    def is_able_to_change_status(self, incident: Incident) -> bool:
        if incident.status == Incident.INCIDENT_STATUS_CANCELED:
            return False
        if incident.status == self.get_incident_status_change_to():
            return False
        return True

    def make_changes_to_incident_according_to_status_change(self, incident: Incident) -> Incident:
        incident.finalized_at = datetime.now()
        incident.incidentresource_set.all().update(exited_from_incident_at=datetime.now())
        incident_creation_notification_manager = IncidentCreationNotificationManager(incident)
        incident_creation_notification_manager.notify_incident_finalization()
        async_to_sync(get_channel_layer().group_send)(str(incident.id),
                                                      {"type": AvailableIncidentTypes.INCIDENT_FINALIZED})
        return incident


class IncidentStatusCancelAPIView(ChangeIncidentStatusAPIView):
    def get_incident_status_change_to(self) -> str:
        return Incident.INCIDENT_STATUS_CANCELED

    def is_able_to_change_status(self, incident: Incident) -> bool:
        if incident.status == Incident.INCIDENT_STATUS_FINALIZED:
            return False
        if incident.status == self.get_incident_status_change_to():
            return False
        return True

    def make_changes_to_incident_according_to_status_change(self, incident: Incident) -> Incident:
        incident.cancelled_at = datetime.now()
        incident.incidentresource_set.all().update(exited_from_incident_at=datetime.now())
        incident_creation_notification_manager = IncidentCreationNotificationManager(incident)
        incident_creation_notification_manager.notify_incident_cancellation()
        async_to_sync(get_channel_layer().group_send)(str(incident.id),
                                                      {"type": AvailableIncidentTypes.INCIDENT_CANCELLED})
        return incident


class ValidateIncidentDetailsAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Validate incident details, Only Admin user",
                         request_body=serializers.ValidateIncidentDetailsSerializer,
                         responses={200: '{ "message": "Incident data is complete" }',
                                    400: "{'message': 'Incident with id: ID does not exist'},"
                                         "{'message': 'Details validation failed. Error: ERROR'}"})
    def post(self, request, incident_id):
        serializer = serializers.ValidateIncidentDetailsSerializer(data=request.data,
                                                                   context={'incident_id': incident_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'Incident data is complete'}),
                                status=status.HTTP_200_OK)


class AddIncidentResourceToIncidentAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Create incident resource",
                         request_body=serializers.CreateUpdateIncidentResourceSerializer,
                         responses={200: "{'message': 'IncidentResource successfully created'}",
                                    400: "{'incident_id': 'Incident is not at Created state'},"
                                         "{'resource_id': 'User resource is not active'},"
                                         "{'resource_id': 'User resource already joined to this Incident'},"
                                         "{'non_field_error': 'Resource of type Container cannot have a related instance of container resource!},"  # noqa 
                                         "{'container_resource_id': 'Container resource must be able to contain resources'}",  # noqa
                                    404: "{'incident_id': 'Incident with id: {incident_id} does not exist'},"
                                         "{'container_resource_id': 'Container resource not found'},"
                                         "{'resource_id': 'Resource not found'}"}, )
    def post(self, request, incident_id, resource_id):
        serializer_context_data = {
            'incident_id': incident_id,
            'resource_id': resource_id
        }

        serializer = serializers.CreateUpdateIncidentResourceSerializer(data=request.data,
                                                                        context=serializer_context_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'IncidentResource successfully created'}))

    @swagger_auto_schema(operation_description="Update incident resource",
                         request_body=serializers.CreateUpdateIncidentResourceSerializer,
                         responses={200: "{'message': 'IncidentResource successfully created'}",
                                    400: "{'incident_id': 'Incident is not at Created state'},"
                                         "{'resource_id': 'User resource is not active'},"
                                         "{'resource_id': 'User resource already joined to this Incident'},"
                                         "{'non_field_error': 'Resource of type Container cannot have a related instance of container resource!},"  # noqa 
                                         "{'container_resource_id': 'Container resource must be able to contain resources'}",  # noqa
                                    404: "{'incident_id': 'Incident with id: {incident_id} does not exist'},"
                                         "{'container_resource_id': 'Container resource not found'},"
                                         "{'resource_id': 'Resource not found'}"}, )
    def put(self, request, incident_id, resource_id):
        serializer_context_data = {
            'incident_id': incident_id,
            'resource_id': resource_id
        }

        serializer = serializers.CreateUpdateIncidentResourceSerializer(data=request.data,
                                                                        context=serializer_context_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'IncidentResource successfully updated'}))

    @swagger_auto_schema(operation_description="Delete incident resource",
                         responses={200: "{'message': 'IncidentResource successfully deleted'}",
                                    400: "{'message': 'Incident is not at Created state'},"
                                         "{'message': 'User resource is not active'}",
                                    404: "{'message': 'Incident not found'},"
                                         "{'message': 'Resource not found'}"}, )
    def delete(self, request, incident_id, resource_id):
        try:
            incident = models.Incident.objects.get(id=incident_id)
        except models.Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Incident not found'}),
                                status=status.HTTP_404_NOT_FOUND)

        if incident.status != incident.INCIDENT_STATUS_STARTED:
            return HttpResponse(json.dumps({'message': 'Incident is not at Created state'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            resource = ResourceProfile.objects.get(id=resource_id)
        except ResourceProfile.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Resource not found'}),
                                status=status.HTTP_404_NOT_FOUND)

        if not resource.user.is_active:
            return HttpResponse(json.dumps({'message': 'User resource is not active'}),
                                status=status.HTTP_400_BAD_REQUEST)

        incident_resource = IncidentResource.objects.get(incident=incident, resource=resource)
        incident_resource.exited_from_incident_at = datetime.now()
        incident_resource.save()

        return HttpResponse(json.dumps({'message': 'IncidentResource successfully updated'}))


class IncidentResourceFilter(django_filters.FilterSet):
    resource__user__username = django_filters.CharFilter(lookup_expr='iexact')
    resource__user__first_name = django_filters.CharFilter(lookup_expr='iexact')
    resource__user__last_name = django_filters.CharFilter(lookup_expr='iexact')
    resource__user__is_active = django_filters.CharFilter(lookup_expr='iexact')
    resource__type__name = django_filters.CharFilter(lookup_expr='iexact')
    incident__status = django_filters.CharFilter(lookup_expr='iexact')
    resource__type__is_able_to_contain_resources = django_filters.BooleanFilter()
    has_no_container_resource = django_filters.BooleanFilter(field_name='container_resource_id', lookup_expr='isnull')
    exited_from_incident_no_date = django_filters.BooleanFilter(field_name='exited_from_incident_at',
                                                                lookup_expr='isnull')

    class Meta:
        model = IncidentResource
        exclude = ['created_at', 'updated_at', 'incident', 'resource', 'container_resource']


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000


class IncidentResourceViewSet(GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = IncidentResource.objects.all()
    serializer_class = IncidentResourceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IncidentResourceFilter
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        incident_id = kwargs.get('incident_id')
        assert incident_id is not None, "incident_id is required"
        try:
            incident = models.Incident.objects.get(id=incident_id)
        except models.Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': 'Incident not found'}),
                                status=status.HTTP_404_NOT_FOUND)

        incident_resources = self.filter_queryset(self.get_queryset()).filter(incident=incident)

        page = self.paginate_queryset(incident_resources)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(incident_resources, many=True)
        return Response(serializer.data)


class IncidentResourceFromResourceListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = IncidentResourceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IncidentResourceFilter

    def get_queryset(self):
        return IncidentResource.objects.filter(resource_id=self.kwargs['resource_id'])
