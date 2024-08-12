from django.contrib import admin

from apps.api.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass
