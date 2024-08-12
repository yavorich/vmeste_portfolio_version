from django.contrib import admin

from apps.api.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
