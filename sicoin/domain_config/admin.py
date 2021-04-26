from django.contrib import admin
from sicoin.domain_config import models


@admin.register(models.SupervisorAlias)
class SupervisorAliasAdmin(admin.ModelAdmin):
    list_display = ("id", "alias")


@admin.register(models.ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_able_to_contain_resources")


@admin.register(models.MapPointDescription)
class MapPointDescriptionsAdmin(admin.ModelAdmin):
    list_display = ("text", "incident_type")


@admin.register(models.IncidentTypeResource)
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
    readonly_fields = ("domain_code", "parsed_json",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
