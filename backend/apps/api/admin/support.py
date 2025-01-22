from django.contrib import admin, messages

from apps.api.models import (
    SupportRequestTheme,
    SupportRequestMessage,
    SupportRequestType,
    SupportAnswer,
)
from apps.api.tasks import send_email_support_answer


class SupportMessageInline(admin.TabularInline):
    model = SupportRequestMessage
    fields = [
        "author",
        "status",
        "theme",
        "get_subject",
        "text",
    ]
    readonly_fields = ("get_subject",)
    classes = ["collapse"]

    @admin.display(description="Объект обращения")
    def get_subject(self, obj):
        if obj.event:
            return obj.event
        if obj.profile:
            return obj.profile
        return None


@admin.register(SupportRequestTheme)
class SupportThemeAdmin(admin.ModelAdmin):
    # inlines = [SupportMessageInline]
    list_display = [
        "name",
        "type",
        "requests_count",
    ]

    @admin.display(description="Кол-во обращений")
    def requests_count(self, obj):
        return obj.request_messages.count()


class SupportAnswerInline(admin.StackedInline):
    model = SupportAnswer
    fields = ("text", "sent")
    readonly_fields = ("sent",)
    extra = 0


@admin.register(SupportRequestMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    inlines = (SupportAnswerInline,)
    fields = ("author", "status", "get_theme", "get_type", "get_subject", "text")
    readonly_fields = ("author", "get_theme", "get_type", "get_subject", "text")
    list_display = [
        "id",
        "author",
        "status",
        "get_type",
        "get_theme",
        "get_subject",
        "text",
    ]
    list_display_links = list_display
    list_filter = ["status", "theme__type", "theme__name"]

    @admin.display(description="Тема")
    def get_theme(self, obj):
        return getattr(obj.theme, "name")

    @admin.display(description="Тип обращения")
    def get_type(self, obj):
        if obj.theme.type:
            return SupportRequestType(obj.theme.type).label
        return None

    @admin.display(description="Объект обращения")
    def get_subject(self, obj):
        if obj.event:
            return obj.event
        if obj.profile:
            return obj.profile
        return None

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        instance = form.instance
        if hasattr(instance, "answer") and not instance.answer.sent:
            if instance.author.email is not None:
                answer = instance.answer
                send_email_support_answer.delay(
                    instance.author.email, instance.pk, answer.text
                )
                answer.sent = True
                answer.save()
                messages.add_message(
                    request, messages.SUCCESS, "Ответ успешно отправлен"
                )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "У пользователя не указана электронная почта",
                )
