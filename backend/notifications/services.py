from enum import Enum

from httpx import AsyncClient, HTTPError
from django.conf import settings

from api.models import User
from notifications.models import Notification


class PushGroup(str, Enum):
    ALL = "all"
    RECS_ENABLED = "recs_enabled"
    PARTICIPANTS = "participants"
    ORGANIZER = "organizer"


def generate_push_notification_body(type, group):
    event_remind_sample = {
        PushGroup.ORGANIZER: "отменить",
        PushGroup.PARTICIPANTS: "не пойти на",
    }
    body = {
        Notification.Type.EVENT_REMIND: (
            "Напоминаем, что событие уже скоро! "
            + f"Вы можете {event_remind_sample.get(group, '')} встречу. "
            + "Успейте принять решение не позднее, чем за 3 часа до начала мероприятия!"
        ),
        Notification.Type.EVENT_CANCELED: (
            "Событие отменено организатором или администрацией."
        ),
        Notification.Type.EVENT_CHANGED: (
            "Событие изменилось! Проверьте актуальную информацию на странице события"
        ),
        Notification.Type.EVENT_REC: (
            "Новое интересное событие! "
            + "Успейте записаться, пока есть свободные места."
        ),
    }
    return body[type]


def get_push_notification_users_list(group, event=None):
    users = User.objects.filter(is_active=True, is_staff=False, sending_push=True)
    if group == PushGroup.ALL:
        return users
    if group == PushGroup.RECS_ENABLED:
        return users.filter(receive_recs=True)
    if group == PushGroup.ORGANIZER:
        return [event.organizer] if event.organizer.sending_push else []
    if group == PushGroup.PARTICIPANTS:
        return users.filter(events__in=event.participants.all())


async def send_fcm_push(token, title, body):
    url = "https://fcm.googleapis.com/fcm/send"
    payload = {
        "registration_ids": [token],
        "content_available": True,
        # "android_channel_id": "default_notification_channel_id",
        "priority": "high",
        "notification": {
            "title": title,
            "body": body,
        },
        "data": {"click_action": "FLUTTER_NOTIFICATION_CLICK"},
        "apns": {"payload": {"aps": {"content_available": 1, "mutable-content": 1}}},
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={settings.FCM_TOKEN}",
    }

    async with AsyncClient() as client:
        try:
            await client.post(url, headers=headers, json=payload)
        except HTTPError:
            pass
