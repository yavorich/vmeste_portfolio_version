from django.contrib import admin

from api.models import Theme, Category


class CategoryInline(admin.TabularInline):
    model = Category


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    inlines = [CategoryInline]
    list_display = ["title", "events_count"]

    @admin.display(description="Кол-во событий")
    def events_count(self, obj):
        return obj.events.count()
