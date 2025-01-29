from django.contrib import admin
from django.contrib.admin.filters import (
    SimpleListFilter,
)
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rangefilter.filters import DateRangeFilterBuilder

from apps.admin_history.admin import site
from core.admin import ManyToManyMixin
from apps.api.models import Event, EventParticipant, User, EventMedia, EventAdminProxy


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant


class EventMediaInline(admin.TabularInline):
    model = EventMedia


class EventStatusFilter(SimpleListFilter):
    title = _("Статус")
    parameter_name = ""

    def lookups(self, request, model_admin):
        return (
            ("past", _("Прошедшие")),
            ("future", _("Будущие")),
            ("close", _("Закрытые")),
            ("archive", _("Архивные")),
        )

    def queryset(self, request, queryset):
        if self.value() == "past":
            return queryset.filter_past()
        if self.value() == "future":
            return queryset.filter_upcoming()
        if self.value() == "close":
            return queryset.filter(is_close_event=True)
        if self.value() == "archive":
            return queryset.filter(Q(is_draft=True) | Q(is_active=False))


class EventForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("total_people") is not None:
            cleaned_data["total_male"] = None
            cleaned_data["total_female"] = None
        return cleaned_data


@admin.register(Event, site=site)
class EventAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [EventParticipantInline, EventMediaInline]
    form = EventForm
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "is_active",
                    "is_close_event",
                    "is_draft",
                    "title",
                    "short_description",
                    "description",
                    "country",
                    "city",
                    "cover",
                    "location",
                    "date",
                    "start_time",
                    "end_time",
                    "theme",
                    "categories",
                    "total_male",
                    "total_female",
                    "total_people",
                    "min_age",
                    "max_age",
                    "did_organizer_marking",
                    "organizer_will_pay",
                ]
            },
        )
    ]
    readonly_fields = ["organizer_will_pay"]
    list_display = [
        "id",
        "is_active",
        "title",
        "date",
        "start_time",
        "end_time",
        "get_notifications",
        "city",
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
        "will_come",
    ]
    # list_editable = [
    #     "is_active",
    #     "title",
    #     "city",
    #     "date",
    #     "start_time",
    #     "end_time",
    #     "theme",
    #     "cover",
    #     "short_description",
    #     "min_age",
    #     "max_age",
    # ]
    list_filter = [
        EventStatusFilter,
        "city",
        "theme",
        "categories",
        ("date", DateRangeFilterBuilder()),
    ]
    search_fields = [
        "title",
        "short_description",
        "location__name",
        "location__address",
    ]
    actions = ["block_events", "unblock_events"]
    date_hierarchy = "date"
    ordering = ("-id",)

    @admin.display(description="Уведомления")
    def get_notifications(self, obj):
        return obj.notifications.count()

    @admin.display(description="Название локации")
    def location_name(self, obj):
        return getattr(obj.location, "name", None)

    @admin.display(description="Мужчины")
    def get_stats_men(self, obj):
        return obj.stats_men

    @admin.display(description="Женщины")
    def get_stats_women(self, obj):
        return obj.stats_women

    @admin.display(description="Адрес")
    def location_address(self, obj):
        return getattr(obj.location, "address", None)

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


@admin.register(EventAdminProxy, site=site)
class EventAdminProxyAdmin(EventAdmin):
    list_display = ("id", "start_datetime", "title")
    list_display_links = list_display
    ordering = ("-start_datetime",)
