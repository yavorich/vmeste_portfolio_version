from django.contrib import admin

from notifications.models import Notification, UserNotification


class UserNotificationsInline(admin.TabularInline):
    model = UserNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    inlines = [UserNotificationsInline]
    list_display = [
        "type",
        "created_at",
        "event",
        "title",
        "body",
    ]
