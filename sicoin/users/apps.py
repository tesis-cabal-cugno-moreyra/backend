from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'sicoin.users'
    verbose_name = 'Users Configuration'

    def ready(self):
        from sicoin.users import signals  # noqa
