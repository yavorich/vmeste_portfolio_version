from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import Occupation


@admin.register(Occupation, site=site)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    list_editable = ["title"]
