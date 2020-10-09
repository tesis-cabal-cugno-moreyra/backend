from django.db.models.signals import post_save
from django.dispatch import receiver

from sicoin.domain_config import models
from sicoin.domain_config.domain_dict_generator import DomainDictGenerator


@receiver(post_save, sender=models.ResourceType)
@receiver(post_save, sender=models.IncidentTypeResource)
@receiver(post_save, sender=models.IncidentType)
@receiver(post_save, sender=models.IncidentAbstraction)
@receiver(post_save, sender=models.MapPointDescription)
@receiver(post_save, sender=models.SupervisorAlias)
@receiver(post_save, sender=models.DomainConfig)
def save_user_profile(sender, instance, **kwargs):
    is_loading_fixtures = bool(kwargs.get('raw'))
    if not is_loading_fixtures:
        domain: models.DomainConfig = instance.domain_config
        parsed_json = DomainDictGenerator(instance.domain_config).to_dict_representation()
        models.DomainConfig.objects.filter(pk=domain.pk).update(parsed_json=parsed_json)
