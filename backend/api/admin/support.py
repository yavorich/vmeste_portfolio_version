from django.contrib import admin

from api.models import SupportRequestTheme, SupportRequestMessage, SupportRequestType


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
    inlines = [SupportMessageInline]
    list_display = [
        "name",
        "type",
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
        "get_type",
        "get_theme",
        "get_subject",
        "text",
    ]
    list_editable = ["status",]
    list_filter = [
        "status",
        "theme__type",
        "theme__name",
    ]

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
