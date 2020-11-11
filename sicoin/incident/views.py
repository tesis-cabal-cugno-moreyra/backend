# from django.shortcuts import render

# Create your views here.

# Create incident

# Data REALLY needed ->
# Pause incident
# Finalize incident
# List filtered incidents DEFAULT=ALL, querystring for additional statuses

import json

from django.http import HttpResponse
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from sicoin.incident import models, serializers
from sicoin.incident.models import Incident
from sicoin.users.models import ResourceProfile


class IncidentCreateListViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = Incident.objects.all()
    serializer_class = serializers.CreateIncidentSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('incident_type__name', 'external_assistance', 'status', 'data_status')

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
                         responses={200: "{'message': 'Changed user status successfully'}",
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


class ValidateIncidentDetailsAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Enable user, Only Admin user",
                         request_body=serializers.ValidateIncidentDetailsSerializer,
                         responses={200: '{ "message": "Incident data is complete" }',
                                    400: "{'message': 'Incident with id: ID does not exist'},"
                                         "{'message': 'Details validation failed. Error: ERROR'}"})
    def post(self, request, format=None):
        serializer = serializers.ValidateIncidentDetailsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'Incident data is complete'}),
                                status=status.HTTP_200_OK)


class AddIncidentResourceToIncidentAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Check of current domain code",
                         responses={200: "{'message': 'IncidentResource successfully created'}",
                                    400: "{'message': 'Incident is not at Created state'},"
                                         "{'message': 'User resource is not active'}",
                                    404: "{'message': 'Incident not found'},"
                                         "{'message': 'Resource not found'}"}, )
    def post(self, request, incident_id, resource_id):
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

        return HttpResponse(json.dumps({'message': 'IncidentResource successfully created'}))
