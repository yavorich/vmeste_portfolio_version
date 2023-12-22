from django.contrib import admin

from api.models import SupportRequestTheme, SupportRequestMessage


class SupportMessageInline(admin.TabularInline):
    model = SupportRequestMessage
    fields = ["author", "status", "subject", "get_subject", "theme", "text"]
    readonly_fields = ("get_subject",)
    classes = ["collapse"]

    @admin.display(description="Объект жалобы")
    def get_subject(self, obj):
        return getattr(obj, obj.subject)


@admin.register(SupportRequestTheme)
class SupportThemeAdmin(admin.ModelAdmin):
    inlines = [SupportMessageInline]
    list_display = [
        "name",
        "requests_count",
    ]

    @admin.display(description="Кол-во обращений")
    def requests_count(self, obj):
        return obj.request_messages.count()


@admin.register(SupportRequestMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author",
        "status",
        "subject",
        "get_subject",
        "theme",
        "text",
    ]
    list_editable = ["status", "theme"]
    list_filter = [
        "status",
        "subject",
        "theme__name",
    ]

    @admin.display(description="Объект жалобы")
    def get_subject(self, obj):
        return getattr(obj, obj.subject)
