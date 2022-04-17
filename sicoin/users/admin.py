from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from sicoin.users import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    pass


@admin.register(models.AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "domain")


@admin.register(models.SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "domain")


@admin.register(models.ResourceProfile)
class ResourceProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "domain", "device", "stats_by_incident")
