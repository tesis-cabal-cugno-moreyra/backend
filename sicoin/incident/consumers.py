import asyncio
import json
from enum import Enum

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from sicoin.geolocation.serializers import MapPointSerializer, TrackPointSerializer
from sicoin.incident.models import Incident
from sicoin.utils import MetaEnum


class AvailableIncidentTypes(str, Enum, metaclass=MetaEnum):
    MAP_POINT = 'map_point'
    TRACK_POINT = 'track_point'
    INCIDENT_FINALIZED = 'incident_finalized'
    INCIDENT_CANCELLED = 'incident_cancelled'


class IncidentConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def _get_incident(self) -> Incident:
        return Incident.objects.get(id=self.incident_id)

    @database_sync_to_async
    def _save_map_point(self, data):
        assert int(data['incidentId']) == int(self.incident_id)

        map_point_serializer = MapPointSerializer(
            data={
                'location': {
                    'type': 'Point',
                    'coordinates': [data['lat'], data['lng']]
                },
                'comment': data['message'],
                'time_created': data['timeCreated'],
            },
            context={
                'incident_id': data['incidentId'],
                'resource_id': data['resourceId']
            }
        )

        if map_point_serializer.is_valid(raise_exception=True):
            map_point = map_point_serializer.save()
            return map_point_serializer.to_representation(map_point)

    @database_sync_to_async
    def _save_track_point(self, data):
        assert int(data['incidentId']) == int(self.incident_id)

        track_point_serializer = TrackPointSerializer(
            data={
                'location': {
                    'type': 'Point',
                    'coordinates': [data['lat'], data['lng']]
                },
                'time_created': data['timeCreated'],
            },
            context={
                'incident_id': data['incidentId'],
                'resource_id': data['resourceId']
            }
        )

        if track_point_serializer.is_valid(raise_exception=True):
            track_point = track_point_serializer.save()
            return track_point_serializer.to_representation(track_point)

    def _generate_tp_data(self, index):
        return {
            "lat": 37.4219284,
            "lng": -122.0840116,
            "message": "Probando websocket 0",
            "incidentId": 1,
            "resourceId": 1,
            "timeCreated": "2021-03-24T22:12:27.469Z"
        }

    def _generate_mp_data(self, index):
        return {
            "lat": 37.4219284,
            "lng": -122.0840116,
            "message": "Probando websocket 0",
            "incidentId": 1,
            "resourceId": 1,
            "timeCreated": "2021-03-24T22:12:27.469Z"
        }

    async def connect(self):
        self.incident_id = self.scope['url_route']['kwargs']['incident_id']
        # Assert existing incident

        # if not self._get_incident().status_is_started:
        #    await self.send({"close": True})

        # Join incident group
        await self.channel_layer.group_add(
            self.incident_id,
            self.channel_name
        )
        await self.accept()

        if not settings.INCIDENT_WS_DATA_GENERATION:
            return

        for i in range(1, 10000):
            # FIXME: How are we going to dump dates?
            if (i % 2) == 0:
                await self.send(
                    json.dumps({
                        'type': AvailableIncidentTypes.TRACK_POINT,
                        'data': self._generate_tp_data(i)
                    }))
            else:
                await self.send(
                    json.dumps({
                        'type': AvailableIncidentTypes.MAP_POINT,
                        'data': self._generate_mp_data(i)
                    }))
            await asyncio.sleep(5)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type not in AvailableIncidentTypes:
            raise Exception(f'Wrong type of message sent: {message_type}')

        await self.channel_layer.group_send(
            self.incident_id,
            {
                'type': message_type,
                'data': text_data_json['data']
            }
        )

    async def map_point(self, event):
        data = event['data']
        # Validate data here
        map_point_repr = await self._save_map_point(data)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'incident_type': AvailableIncidentTypes.MAP_POINT,
            'data': map_point_repr
        }))

    async def track_point(self, event):
        data = event['data']
        # Validate data here
        track_point_repr = await self._save_track_point(data)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'incident_type': AvailableIncidentTypes.TRACK_POINT,
            'data': track_point_repr
        }))

    async def incident_finalized(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event_type': 'incident_finalized',
            'incident_id': self.incident_id
        }))

    async def incident_cancelled(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event_type': 'incident_cancelled',
            'incident_id': self.incident_id
        }))
