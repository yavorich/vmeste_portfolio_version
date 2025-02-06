from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import Docs


@admin.register(Docs, site=site)
class DocsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return Docs.objects.count() < len(Docs.Name.values)
