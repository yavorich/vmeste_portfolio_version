from django.contrib import admin

from apps.api.models import Docs


@admin.register(Docs)
class DocsAdmin(admin.ModelAdmin):
    pass
