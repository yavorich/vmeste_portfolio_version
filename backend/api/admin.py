from django.contrib import admin
from django_celery_results.admin import TaskResult, GroupResult

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    fields = ["name"]


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    fields = ["name", "country"]


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    fields = ["title"]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ["title", "theme"]


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "city", "address"]


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Docs)
class DocsAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportTheme)
class SupportThemeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Occupation)
class OccupationAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)
