from celery import shared_task
from asgiref.sync import async_to_sync

from notifications.services import (
    generate_push_notification_body,
    get_push_notification_users_list,
)  # , send_fcm_push
from api.models import Event
from notifications.models import Notification, UserNotification


@shared_task
def create_notifications_task(pk, type):
    kwargs = {"event": pk, "type": type}
    return Notification.objects.create(**kwargs)


@shared_task
def send_push_notifications_task(data, groups):
    event = Event.objects.get(pk=data["event"]) if data.get("event") else None
    if data["type"] == Notification.Type.ADMIN:
        body = data["body"]
    else:
        body = {
            group: generate_push_notification_body(data["type"], group)
            for group in groups
        }
    users = {
        group: get_push_notification_users_list(data["type"], group, event)
        for group in groups
    }
    notifications = []
    for group in groups:
        for user in users[group]:
            notification = UserNotification.objects.create(
                user=user, notification=data["id"], body=body[group]
            )
            notifications.append(notification)

    async_to_sync(send_push_notifications)(users, notifications)
    return "Success send push notifications"


async def send_push_notifications(users, notifications):
    pass
    # async for user, notification in zip(users, notifications):
    #     push_token = PushToken.objects.filter(user=user)
    #     await send_fcm_push(
    #         push_token.token, notification.notification.title, notification.body
    #     )
