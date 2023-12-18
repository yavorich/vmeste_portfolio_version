from django.contrib import admin

from notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fields = ("title", "body", "date")
    readonly_fields = ("date",)
    list_display = ("date", "short_text")
    list_display_links = ("date", "short_text")
    search_fields = ("text",)
    ordering = ("-date",)
    show_full_result_count = False

    @admin.display(description="Текст")
    def short_text(self, obj):
        return obj.short_text

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
