import logging

from sicoin.incident.models import Incident
from sicoin.users.models import User


class IncidentCreationNotificationManager:
    def __init__(self, incident: Incident):
        self.incident = incident

    def notify_incident_creation(self):
        active_resources = self.incident.domain_config.resourceprofile_set.filter(user__is_active=True,
                                                                                  device__isnull=False)
        for resource in active_resources:
            title = 'Incidente creado!'
            body = 'Revisa la lista de incidentes para más información'
            resource.device.send_message(title=title, body=body)

    def notify_incident_cancellation(self):
        incident_resources_from_incident = self.incident.incidentresource_set.filter(
            resource__user__is_active=True, resource__device__isnull=False)

        for incident_resource in incident_resources_from_incident:
            title = 'Incidente cancelado!'
            body = 'Revisa la lista de incidentes para más información'
            incident_resource.resource.device.send_message(title=title, body=body)

    def notify_incident_finalization(self):
        incident_resources_from_incident = self.incident.incidentresource_set.filter(
            resource__user__is_active=True, resource__device__isnull=False)

        for incident_resource in incident_resources_from_incident:
            title = 'Incidente Finalizado!'
            body = 'Revisa la lista de incidentes para más información'
            incident_resource.device.send_message(title=title, body=body)


class UserStatusChangeNotificationManager:
    def __init__(self, user):
        self._user = user

    def notify_user_status_change(self):
        if self._user.is_active:
            self._notify_user_status_change_to_active()
        else:
            self._notify_user_status_change_to_not_active()

    def _notify_user_status_change_to_active(self):
        try:
            self._user.resourceprofile.notify_resource_user_activation()
        except User.resourceprofile.RelatedObjectDoesNotExist as nonexistent_profile:
            logging.info(f'Nonexistent resource profile for user {self._user}', nonexistent_profile)

    def _notify_user_status_change_to_not_active(self):
        try:
            self._user.resourceprofile.notify_resource_user_deactivation()
        except User.resourceprofile.RelatedObjectDoesNotExist as nonexistent_profile:
            logging.info(f'Nonexistent resource profile for user {self._user}', nonexistent_profile)
