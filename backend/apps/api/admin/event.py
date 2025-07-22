from django.contrib import admin
from django.contrib.admin.filters import (
    SimpleListFilter,
)
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rangefilter.filters import DateRangeFilterBuilder

from apps.admin_history.admin import site
from core.admin import ManyToManyMixin
from apps.api.models import Event, EventParticipant, EventMedia, EventAdminProxy, User
from core.utils.short_text import short_text


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
                    "sign_price",
                ]
            },
        )
    ]
    readonly_fields = ["sign_price"]
    list_display = [
        "id",
        "_is_active",
        "title",
        "_date",
        "_start_time",
        "_end_time",
        "get_notifications",
        "city",
        "theme",
        "get_categories",
        "_cover",
        "location_name",
        "location_address",
        "get_stats_people",
        "short_description",
        "min_age",
        "max_age",
        "will_come",
    ]
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

    @admin.display(description="Актив.", boolean=True)
    def _is_active(self, obj):
        return obj.is_active

    @admin.display(description="Дата")
    def _date(self, obj):
        return obj.date.strftime("%d.%m.%y")

    @admin.display(description="Начало")
    def _start_time(self, obj):
        return obj.start_time

    @admin.display(description="Конец")
    def _end_time(self, obj):
        return obj.end_time

    @admin.display(description="Увед.")
    def get_notifications(self, obj):
        return obj.notifications.count()

    @admin.display(description="Обложка")
    def _cover(self, obj):
        if obj.cover:
            return mark_safe(
                f'<a href="{obj.cover.url}">{short_text(obj.cover.name, 20)}</a>'
            )
        return ""

    @admin.display(description="Локация")
    def location_name(self, obj):
        return getattr(obj.location, "name", None)

    @admin.display(description="Участники")
    def get_stats_people(self, obj):
        return obj.stats_people

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
