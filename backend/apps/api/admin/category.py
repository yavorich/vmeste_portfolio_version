from django.contrib import admin

from apps.api.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "theme", "events_count"]

    @admin.display(description="Кол-во событий")
    def events_count(self, obj):
        return obj.events.count()
