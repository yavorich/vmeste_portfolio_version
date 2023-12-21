from django.contrib import admin

from api.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass
