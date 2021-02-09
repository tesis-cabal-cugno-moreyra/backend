import logging
from sicoin.users.models import User


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
            self._user.resourceprofile.notify_resource_user_activation()
        except User.resourceprofile.RelatedObjectDoesNotExist as nonexistent_profile:
            logging.info(f'Nonexistent resource profile for user {self._user}', nonexistent_profile)
