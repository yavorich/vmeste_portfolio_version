from django.contrib import admin

from api.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
