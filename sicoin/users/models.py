import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from sicoin.domain_config.models import DomainConfig, SupervisorAlias, ResourceType
from sicoin.users.enums import ValidRoles


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    domain = models.ForeignKey(DomainConfig, on_delete=models.PROTECT, null=True, blank=True)

    @property
    def role(self):
        return ValidRoles.ADMINISTRATOR

    def __str__(self):
        return f"username: {self.user.username}, type: Admin"


class SupervisorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    alias = models.ForeignKey(SupervisorAlias, on_delete=models.PROTECT)
    domain = models.ForeignKey(DomainConfig, on_delete=models.PROTECT)

    @property
    def role(self):
        return ValidRoles.SUPERVISOR

    def __str__(self):
        return f"username: {self.user.username}, domain: {self.domain.domain_name}, type: Supervisor, " \
               f"alias: {self.alias.alias}"


class ResourceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    domain = models.ForeignKey(DomainConfig, on_delete=models.PROTECT)

    @property
    def role(self):
        return ValidRoles.RESOURCE

    def __str__(self):
        return f"username: {self.user.username}, domain: {self.domain.domain_name}, type: Resource, " \
               f"resource type: {self.type.name}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
