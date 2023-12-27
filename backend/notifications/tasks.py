from celery import shared_task
from asgiref.sync import async_to_sync

from notifications.services import (
    generate_push_notification_body,
    get_push_notification_users_list,
)  # , send_fcm_push
from notifications.models import Notification, UserNotification
from api.models import Event


@shared_task
def create_notifications_task(pk, type):
    event = Event.objects.get(pk=pk)
    Notification.objects.create(event=event, type=type)
    return f"Notification of type={type} was created"


@shared_task
def send_push_notifications_task(pk, groups):
    notification = Notification.objects.get(pk=pk)
    event = getattr(notification, "event", None)
    if notification.type == Notification.Type.ADMIN:
        body = {group: notification.body for group in groups}
    else:
        body = {
            group: generate_push_notification_body(notification.type, group)
            for group in groups
        }
    users = {group: get_push_notification_users_list(group, event) for group in groups}
    user_notifications = []
    for group in groups:
        for user in users[group]:
            user_notification = UserNotification.objects.create(
                user=user, notification=notification, body=body[group]
            )
            user_notifications.append(user_notification)

    async_to_sync(send_push_notifications)(users, user_notifications)

    if notification.type == Notification.Type.EVENT_CANCELED:
        event.participants.all().delete()

    return "Success send push notifications"


async def send_push_notifications(users, notifications):
    pass
    # async for user, notification in zip(users, notifications):
    #     push_token = PushToken.objects.filter(user=user)
    #     await send_fcm_push(
    #         push_token.token, notification.notification.title, notification.body
    #     )
