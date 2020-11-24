import json
import logging

from django.http import HttpResponse, JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from sicoin.geolocation.models import MapPoint, TrackPoint
from sicoin.geolocation.serializers import MapPointSerializer, TrackPointSerializer
from sicoin.incident.models import Incident
from django.utils import timezone

resource_id_query_parameter = openapi.Parameter('resource_id', openapi.IN_QUERY,
                                                description="Related resource id", type=openapi.TYPE_INTEGER)

timedelta_in_seconds_query_parameter = openapi.Parameter('timedelta_in_seconds', openapi.IN_QUERY,
                                                         description="filter by created on the last X seconds",
                                                         type=openapi.TYPE_INTEGER)


class GetMapPointsFromIncident(APIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, incident: Incident):
        queryset = MapPoint.objects.filter(incident=incident)
        resource_id = self.request.query_params.get('resource_id', None)
        if resource_id is not None:
            queryset = queryset.filter(incident_resource__resource_id=resource_id)

        timedelta_in_seconds = self.request.query_params.get('timedelta_in_seconds', None)
        if timedelta_in_seconds is not None:
            now = timezone.datetime.now()
            try:
                earlier = now - timezone.timedelta(seconds=int(timedelta_in_seconds))
                queryset = queryset.filter(time_created__range=(earlier, now))
            except ValueError as value_error:
                logging.debug(value_error)
        return queryset

    @swagger_auto_schema(operation_description="List Map Points for related incident",
                         manual_parameters=[resource_id_query_parameter, timedelta_in_seconds_query_parameter],
                         responses={200: "[\n"
                                         "{\n"
                                         "  'location': GeometryField,\n"
                                         "  'collected_at': instance.time_created,\n"
                                         "  'internal_type': 'MapPoint',\n"
                                         "  'resource_id': instance.incident_resource.resource_id,\n"
                                         "  'comment': instance.description_text\n"
                                         "}, ...\n"
                                         "]",
                                    400: "{'message': 'Incident with id {ID} does not exists'},\n"
                                         "{'message': 'Map points for Incident with id {ID} are nonexistent'}"})
    def get(self, request, incident_id):
        if not incident_id:
            return HttpResponse(json.dumps({'message': 'Incident id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Incident with id {incident_id} '
                                                       f'does not exists'}),
                                status=status.HTTP_404_NOT_FOUND)

        try:
            map_points_from_incident = self.get_queryset(incident)
        except MapPoint.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Map points for Incident with id {incident_id} '
                                                       f'are nonexistent'}),
                                status=status.HTTP_400_BAD_REQUEST)
        map_points_from_incident_serialized = []
        for map_point in map_points_from_incident:
            map_points_from_incident_serialized.append(MapPointSerializer().to_representation(map_point))
        return JsonResponse(map_points_from_incident_serialized, safe=False)


class CreateMapPoint(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Create MapPoint, Only Resource user",
                         request_body=MapPointSerializer,
                         responses={200: '{ "message": "MapPoint successfully created" }',
                                    400: "{'incident_id': 'Incident with id: ID does not exist'},\n"
                                         "{'incident_id': 'Incident with id: ID is not at Created state'},\n"
                                         "{'resource_id': 'Resource with id: ID does not exist'},\n"
                                         "{'resource_id': 'User related to Resource with id: ID is not active'}"})
    def post(self, request, incident_id, resource_id):
        serializer = MapPointSerializer(data=request.data,
                                        context={'incident_id': incident_id, 'resource_id': resource_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'MapPoint successfully created'}),
                                status=status.HTTP_200_OK)


class GetTrackPointsFromIncident(APIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, incident: Incident):
        queryset = TrackPoint.objects.filter(incident=incident)
        resource_id = self.request.query_params.get('resource_id', None)
        if resource_id is not None:
            queryset = queryset.filter(incident_resource__resource_id=resource_id)

        timedelta_in_seconds = self.request.query_params.get('timedelta_in_seconds', None)
        if timedelta_in_seconds is not None:
            now = timezone.datetime.now()
            try:
                earlier = now - timezone.timedelta(seconds=int(timedelta_in_seconds))
                queryset = queryset.filter(time_created__range=(earlier, now))
            except ValueError as value_error:
                logging.debug(value_error)
        return queryset

    @swagger_auto_schema(operation_description="List Track Points for related incident",
                         manual_parameters=[resource_id_query_parameter, timedelta_in_seconds_query_parameter],
                         responses={200: "[\n"
                                         "{\n"
                                         "  'location': GeometryField,\n"
                                         "  'collected_at': instance.time_created,\n"
                                         "  'internal_type': 'TrackPoint',\n"
                                         "  'resource_id': instance.incident_resource.resource_id,\n"
                                         "}, ...\n"
                                         "]",
                                    400: "{'message': 'Incident with id {ID} does not exists'},\n"
                                         "{'message': 'Track points for Incident with id {ID} are nonexistent'}"})
    def get(self, request, incident_id):
        if not incident_id:
            return HttpResponse(json.dumps({'message': 'Incident id invalid or empty'}),
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Incident with id {incident_id} '
                                                       f'does not exists'}),
                                status=status.HTTP_404_NOT_FOUND)

        try:
            map_points_from_incident = self.get_queryset(incident)
        except TrackPoint.DoesNotExist:
            return HttpResponse(json.dumps({'message': f'Track points for Incident with id {incident_id} '
                                                       f'are nonexistent'}),
                                status=status.HTTP_400_BAD_REQUEST)
        map_points_from_incident_serialized = []
        for map_point in map_points_from_incident:
            map_points_from_incident_serialized.append(TrackPointSerializer().to_representation(map_point))
        return JsonResponse(map_points_from_incident_serialized, safe=False)


class CreateTrackPoint(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(operation_description="Create TrackPoint, Only Resource user",
                         request_body=TrackPointSerializer,
                         responses={200: '{ "message": "TrackPoint successfully created" }',
                                    400: "{'incident_id': 'Incident with id: ID does not exist'},\n"
                                         "{'incident_id': 'Incident with id: ID is not at Created state'},\n"
                                         "{'resource_id': 'Resource with id: ID does not exist'},\n"
                                         "{'resource_id': 'User related to Resource with id: ID is not active'}"})
    def post(self, request, incident_id, resource_id):
        serializer = TrackPointSerializer(data=request.data,
                                          context={'incident_id': incident_id, 'resource_id': resource_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'TrackPoint successfully created'}),
                                status=status.HTTP_200_OK)
