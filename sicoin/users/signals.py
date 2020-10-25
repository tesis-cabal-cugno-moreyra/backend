from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import User


@receiver(pre_save, sender=User)
def set_new_user_inactive(sender, instance, **kwargs):
    if instance._state.adding is True:
        # Log here!
        instance.is_active = False
