from django.contrib import admin

from apps.api.models import EventFastFilter


@admin.register(EventFastFilter)
class EventFastFilterAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "name"]
    list_editable = ["is_active"]
