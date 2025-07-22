from django.contrib import admin

from apps.admin_history.admin import site
from apps.api.models import Category


@admin.register(Category, site=site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "events_count"]

    @admin.display(description="Кол-во событий")
    def events_count(self, obj):
        return obj.events.count()
