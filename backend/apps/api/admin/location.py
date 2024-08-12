from django.contrib import admin

from apps.api.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "cover",
        "country",
        "city",
        "address",
        "status",
        "discount",
    ]
    list_editable = ["name", "status"]
