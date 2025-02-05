from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.admin_history.admin import site
from apps.api.models import Location
from core.utils.short_text import short_text


@admin.register(Location, site=site)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "_cover",
        "country",
        "city",
        "_address",
        "user",
        "status",
        "discount",
    ]

    @admin.display(description="Обложка")
    def _cover(self, obj):
        if obj.cover:
            return mark_safe(
                f'<a href="{obj.cover.url}">{short_text(obj.cover.name, 20)}</a>'
            )
        return ""

    @admin.display(description="Адрес")
    def _address(self, obj):
        return short_text(obj.address, 30)
