from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import Country


@admin.register(Country, site=site)
class CountryAdmin(admin.ModelAdmin):
    pass
