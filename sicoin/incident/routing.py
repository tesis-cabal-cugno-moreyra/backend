from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/incident/(?P<incident_id>\w+)/$', consumers.IncidentConsumer),
    re_path(r'ws/incident/$', consumers.IncidentListConsumer),
    # re_path(r'ws/incident/(?P<indicent_id>\d+)/resources/$', consumers.IncidentResourcesConsumer),
]
