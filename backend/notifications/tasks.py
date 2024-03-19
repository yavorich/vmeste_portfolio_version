from celery import shared_task
from asgiref.sync import async_to_sync

from api.models import Event
from notifications.models import GroupNotification, UserNotification, PushToken
from notifications.services import send_fcm_push


@shared_task
def user_notifications_task(pk):
    notification = GroupNotification.objects.get(pk=pk)
    users = notification.get_users()
    for user in users:
        user_notification = UserNotification.objects.create(
            notification=notification,
            event=notification.event,
            user=user,
        )
        async_to_sync(send_push_notification)(user_notification)
    if notification.type == GroupNotification.Type.EVENT_CANCELED:
        notification.event.participants.filter(is_organizer=False).delete()


async def send_push_notification(notification: UserNotification):
    async for push_token in PushToken.objects.filter(user=notification.user):
        await send_fcm_push(push_token.token, notification.title, notification.body)


@shared_task
def create_daily_event_notifications():
    event = Event.objects.filter_has_free_places().order_by("-free_places").first()
    GroupNotification.objects.create(event=event, type=GroupNotification.Type.EVENT_REC)
    return f"Notification of type={type} was created"  # REVIEW: type - функция
