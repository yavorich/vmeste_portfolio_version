from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import EventFastFilter


@admin.register(EventFastFilter, site=site)
class EventFastFilterAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "name"]
    list_editable = ["is_active"]
