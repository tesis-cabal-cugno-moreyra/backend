import json

from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from sicoin.geolocation.models import MapPoint
from sicoin.geolocation.serializers import MapPointSerializer
from sicoin.incident.models import Incident


class GetMapPointsFromIncident(APIView):
    permission_classes = (AllowAny,)

    # @swagger_auto_schema(operation_description="Change incident status to Cancelled or Finalized",
    #                      responses={200: "{'message': 'Changed incident status successfully'}",
    #                                 400: "{'message': 'Incident with id {ID} does not exists'},"
    #                                      "{'message': 'Incident status as --- already set'}"})
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
            map_points_from_incident = MapPoint.objects.filter(incident=incident)
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
                                    400: "{'message': 'Incident with id: ID does not exist'},"
                                         "{'message': 'Details validation failed. Error: ERROR'}"})
    def post(self, request, incident_id, resource_id):
        serializer = MapPointSerializer(data=request.data,
                                        context={'incident_id': incident_id, 'resource_id': resource_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(json.dumps({'message': 'MapPoint successfully created'}),
                                status=status.HTTP_200_OK)
