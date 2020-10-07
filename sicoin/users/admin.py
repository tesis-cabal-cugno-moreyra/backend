from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from ..domain_config import models


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


@admin.register(models.SupervisorAlias)
class SupervisorAliasAdmin(admin.ModelAdmin):
    list_display = ("id", "alias")


@admin.register(models.ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(models.MapPointDescriptions)
class MapPointDescriptionsAdmin(admin.ModelAdmin):
    list_display = ("text", "incident_type")


@admin.register(models.IncidentTypeResources)
class IncidentTypeResourcesAdmin(admin.ModelAdmin):
    list_display = ("incident_type", "resource_type")


@admin.register(models.IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "abstraction")


@admin.register(models.IncidentAbstraction)
class IncidentAbstractionAdmin(admin.ModelAdmin):
    list_display = ("alias", "domain_config")


@admin.register(models.DomainConfig)
class DomainConfigAdmin(admin.ModelAdmin):
    list_display = ("domain_name", "admin_alias", "domain_code")
