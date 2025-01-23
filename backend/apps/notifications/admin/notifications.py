from django.contrib import admin

from apps.admin_history.admin import site
from apps.notifications.models import GroupNotification, UserNotification


class UserNotificationsInline(admin.TabularInline):
    model = UserNotification


@admin.register(GroupNotification, site=site)
class GroupNotificationAdmin(admin.ModelAdmin):
    inlines = [UserNotificationsInline]
    list_display = [
        "type",
        "created_at",
        "event",
        "title",
        "body",
    ]


@admin.register(UserNotification, site=site)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "event",
        "title",
        "body",
        "created_at",
    ]
