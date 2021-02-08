import asyncio
import json
from enum import Enum

import channels
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from sicoin.incident.models import Incident
from sicoin.incident.serializers import ListIncidentSerializer
from sicoin.utils import MetaEnum


class AvailableIncidentTypes(str, Enum, metaclass=MetaEnum):
    MAP_POINT = 'map_point'
    TRACK_POINT = 'track_point'


class IncidentConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def _get_incident(self) -> Incident:
        return Incident.objects.get(id=self.incident_id)

    def _generate_tp_data(self, index):
        return {
            "location": {
                "type": "Point",
                "coordinates": [
                    -31.425117 + index / 10000,
                    -62.086124 + index / 10000
                ]
            },
            "collected_at": "2020-11-26T21:19:55.953Z",
            "internal_type": "MapPoint",
            "resource": {
                "id": 11,
                "user": {
                    "id": "f196f272-c272-4def-b149-6d0fac71ea14",
                    "email": "carlioss@carlioss.com",
                    "username": "ldiaz",
                    "first_name": "Laura",
                    "last_name": "Díaz",
                    "is_active": True
                },
                "domain": {
                    "id": 1,
                    "created_at": "2020-09-28T00:26:36+0000",
                    "updated_at": "2020-11-05T14:44:44+0000",
                    "domain_name": "DominioPersonalizado",
                    "admin_alias": "Administrador"
                },
                "type": {
                    "id": 1,
                    "created_at": "2020-09-28T00:26:36+0000",
                    "updated_at": "2020-09-28T00:26:36+0000",
                    "name": "Bombero",
                    "domain_config": 1
                }
            }
        }

    def _generate_mp_data(self, index):
        return {
            "location": {
                "type": "Point",
                "coordinates": [
                    -31.425117 + index / 10000,
                    -62.086124 + index / 10000
                ]
            },
            "collected_at": "2020-11-26T21:19:55.953Z",
            "internal_type": "TrackPoint",
            "resource": {
                "id": 11,
                "user": {
                    "id": "f196f272-c272-4def-b149-6d0fac71ea14",
                    "email": "carlioss@carlioss.com",
                    "username": "ldiaz",
                    "first_name": "Laura",
                    "last_name": "Díaz",
                    "is_active": True
                },
                "domain": {
                    "id": 1,
                    "created_at": "2020-09-28T00:26:36+0000",
                    "updated_at": "2020-11-05T14:44:44+0000",
                    "domain_name": "DominioPersonalizado",
                    "admin_alias": "Administrador"
                },
                "type": {
                    "id": 1,
                    "created_at": "2020-09-28T00:26:36+0000",
                    "updated_at": "2020-09-28T00:26:36+0000",
                    "name": "Bombero",
                    "domain_config": 1
                }
            },
            "comment": "string"
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

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'incident_type': AvailableIncidentTypes.MAP_POINT,
            'data': data
        }))

    async def track_point(self, event):
        data = event['data']
        # Validate data here

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'incident_type': AvailableIncidentTypes.MAP_POINT,
            'data': data
        }))


class IncidentListConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def _get_incidents_status_created(self) -> ListIncidentSerializer:
        return ListIncidentSerializer(Incident.started_incidents.all(), many=True).data

    async def connect(self):
        await self.channel_layer.group_add(
            'incident_list',
            self.channel_name
        )
        await self.accept()
        # Note: This could be a lot better, in terms of performance. Maybe, if we:
        # 1. retrieve via GET the list of incidents, and
        # 2. Send data only from the created incident
        # This would work a lot better, as we should not seek for the whole list of incidents every time.
        # Also, if we delete an incident from the shown list, we may send the incident id, and delete it in
        # the app's incident list, if needed.
        await self.channel_layer.group_send(
            'incident_list',
            {
                'type': 'update_incident_list'
            }
        )

    async def update_incident_list(self, event):
        await self.send(text_data=json.dumps({
            'incident_list': (await self._get_incidents_status_created())
        }))


@receiver(post_save, sender=Incident)
def update_incident_list_on_new_incident(sender: Incident, **kwargs):
    # If needed: Create and send messages, related with the sender, and according to status
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'incident_list',
        {
            'type': 'update_incident_list'
        }
    )
