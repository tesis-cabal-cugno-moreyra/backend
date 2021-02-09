from django.core.management.base import BaseCommand
from fcm_django.models import FCMDevice


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('registration_id', type=str, help='Registration ID of the device to send a message')
        parser.add_argument('title', type=str, help='Title of the message')
        parser.add_argument('body', type=str, help='Body of the message')

    def handle(self, *args, **options):
        registration_id = options['registration_id']
        title = options['title']
        body = options['body']

        device = FCMDevice(registration_id=registration_id, type='android')

        device.send_message(title=title, body=body)
