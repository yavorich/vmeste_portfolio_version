from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from chat.models import Chat, Message, Event


class ChatStatusFilter(SimpleListFilter):
    title = _("Статус события")
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
            return queryset.filter(event__in=Event.objects.filter_past())
        if self.value() == "future":
            return queryset.filter(event__in=Event.objects.filter_upcoming())
        if self.value() == "close":
            return queryset.filter(event__is_close_event=True)
        if self.value() == "archive":
            return queryset.filter(Q(event__is_draft=True) | Q(event__is_active=False))


class ChatMessagesInline(admin.TabularInline):
    model = Message
    exclude = ["is_info", "is_incoming"]

    def get_queryset(self, request):
        qs = super(ChatMessagesInline, self).get_queryset(request)
        return qs.filter(is_info=False)


@admin.register(Chat)
class ChatModel(admin.ModelAdmin):
    inlines = [ChatMessagesInline]
    list_display = [
        "event_id",
        "event",
        "messages_count",
        "last_message_time",
    ]
    list_filter = [
        ChatStatusFilter,
    ]

    @admin.display(description="ID")
    def event_id(self, obj):
        return obj.event.id

    @admin.display(description="Кол-во сообщений")
    def messages_count(self, obj):
        return obj.messages.filter(is_info=False).count()

    @admin.display(description="Время последнего сообщения")
    def last_message_time(self, obj):
        messages = obj.messages.filter(is_info=False)
        if messages.exists():
            return messages.latest().sent_at
        return None
