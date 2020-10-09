from django.apps import AppConfig


class DomainConfigConfig(AppConfig):
    name = 'sicoin.domain_config'
    verbose_name = 'Domain Configuration'

    def ready(self):
        from sicoin.domain_config import signals  # noqa
