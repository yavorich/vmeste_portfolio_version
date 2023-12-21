from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from core.admin import ManyToManyMixin
from api.models import Event, EventParticipant, User


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant


@admin.register(Event)
class EventAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [EventParticipantInline]
    list_display = [
        "id",
        "is_active",
        "title",
        "get_notifications",
        "city",
        "date",
        "start_time",
        "end_time",
        "theme",
        "get_categories",
        "cover",
        "location_name",
        "location_address",
        "get_stats_men",
        "get_stats_women",
        "short_description",
        "min_age",
        "max_age",
        "organizer",
        "will_come",
    ]
    list_editable = [
        "is_active",
        "title",
        "city",
        "date",
        "start_time",
        "end_time",
        "theme",
        "cover",
        "short_description",
        "min_age",
        "max_age",
        "organizer",
    ]
    list_filter = [
        "city",
        "theme",
        "categories__title",
        ("date", DateFieldListFilter),
    ]
    search_fields = [
        "title",
        "short_description",
        "location__name",
        "location__address",
    ]
    actions = ["block_events", "unblock_events"]

    @admin.display(description="Уведомления")
    def get_notifications(self, obj):
        return self.links_to_objects(obj.notifications.all())

    @admin.display(description="Название локации")
    def location_name(self, obj):
        return obj.location.name

    @admin.display(description="Мужчины")
    def get_stats_men(self, obj):
        return obj.stats_men

    @admin.display(description="Женщины")
    def get_stats_women(self, obj):
        return obj.stats_women

    @admin.display(description="Адрес")
    def location_address(self, obj):
        return obj.location.address

    @admin.display(description="Пойдут")
    def will_come(self, obj):
        return self.links_to_objects(User.objects.filter(events__event=obj))

    @admin.display(description="Категории")
    def get_categories(self, obj):
        return self.links_to_objects(obj.categories.all())

    @admin.action(description="Заблокировать выбранные события")
    def block_events(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать выбранные события")
    def unblock_events(self, request, queryset):
        queryset.update(is_active=True)
