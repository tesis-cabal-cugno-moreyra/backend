# from django.shortcuts import render

# Create your views here.

# Create incident

# Data REALLY needed ->
# Pause incident
# Finalize incident
# List filtered incidents DEFAULT=ALL, querystring for additional statuses

import json

from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from sicoin.incident import models
from sicoin.users.models import ResourceProfile


class AddIncidentResourceToIncidentAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Check of current domain code",
                         responses={200: "{'message': 'IncidentResource successfully created'}",
                                    400: "{'message': 'Incident is not at Created state'},"
                                         "{'message': 'User resource is not active'}",
                                    404: "{'message': 'Incident not found'},"
                                         "{'message': 'Resource not found'}"},)
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
