from django.contrib import admin

from api.models import Occupation


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    list_editable = ["title"]
