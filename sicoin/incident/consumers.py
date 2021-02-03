import asyncio
import json
from enum import Enum

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from sicoin.utils import MetaEnum


class AvailableIncidentTypes(str, Enum, metaclass=MetaEnum):
    MAP_POINT = 'map_point'
    TRACK_POINT = 'track_point'


class IncidentConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def _generate_incident_data(self, index):
        return {
        "location": {
            "type": "Point",
            "coordinates": [
                -31.425117 + index/10000,
                -62.086124 + index/10000
            ]
        },
        "collected_at": "2020-11-26T21:19:55.953Z",
        "internal_type": "MapPoint",
        "resource_id": {
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

    async def connect(self):
        self.incident_id = self.scope['url_route']['kwargs']['incident_id']
        # Assert existing incident

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
            await self.send(json.dumps(await self._generate_incident_data(index=i)))
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


# Data could be as follows:
"""
VALIDATE DATA IN FE
Resource Data:

{
  "id": 11,
  "user": {
    "id": "f196f272-c272-4def-b149-6d0fac71ea14",
    "email": "carlioss@carlioss.com",
    "username": "ldiaz",
    "first_name": "Laura",
    "last_name": "Díaz",
    "is_active": true
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
[
    {
        "location": {
            "type": "Point",
            "coordinates": [
                -31.425117,
                -62.086124
            ]
        },
        "collected_at": "2020-11-26T21:19:55.953Z",
        "internal_type": "MapPoint",
        "resource_id": {
              "id": 11,
              "user": {
                "id": "f196f272-c272-4def-b149-6d0fac71ea14",
                "email": "carlioss@carlioss.com",
                "username": "ldiaz",
                "first_name": "Laura",
                "last_name": "Díaz",
                "is_active": true
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
    },
    {
        "location": {
            "type": "Point",
            "coordinates": [
                -31.42512,
                -62.0862
            ]
        },
        "collected_at": "2020-11-26T21:20:18.039Z",
        "internal_type": "MapPoint",
        "resource_id": 9,
        "comment": "string" Only for MP
    }
]
"""
