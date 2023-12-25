from django.contrib import admin

from notifications.models import Notification, UserNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "created_at",
        "event",
        "title",
        "body",
    ]


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "notification",
        "user",
        "body",
        "read",
    ]
