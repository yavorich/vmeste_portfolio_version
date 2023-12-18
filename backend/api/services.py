import random
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from httpx import AsyncClient, HTTPError
from django.conf import settings

from api.models import Event
from api.tasks import send_mail_confirmation_code


def generate_confirmation_code():
    return "".join([str(random.randint(0, 9)) for _ in range(5)])


def send_confirmation_code(user, confirm_type):
    if confirm_type == "mail":
        send_mail_confirmation_code.delay(user.email, user.confirmation_code)
    elif confirm_type == "phone":
        pass  # нужен смс-сервис


def get_event_object(id):
    if id.isdigit():
        event = get_object_or_404(Event, id=id)
        if event.is_close_event:
            raise PermissionDenied("Закрытые события доступны только по uuid")
        return event

    return get_object_or_404(Event, uuid=id)


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
