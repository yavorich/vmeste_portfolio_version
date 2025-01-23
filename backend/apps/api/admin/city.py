from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import City


@admin.register(City, site=site)
class CityAdmin(admin.ModelAdmin):
    pass
