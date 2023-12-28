from django.contrib import admin

from api.models import Docs


@admin.register(Docs)
class DocsAdmin(admin.ModelAdmin):
    pass
