from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import Docs


@admin.register(Docs, site=site)
class DocsAdmin(admin.ModelAdmin):
    pass
