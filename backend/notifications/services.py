from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from httpx import AsyncClient, HTTPError

from config.settings import FCM_TOKEN

channel_layer = get_channel_layer()


@async_to_sync
async def send_ws_notification(notification: dict, user_pk: int):
    await asend_ws_notification(notification, user_pk, channel_layer)


async def asend_ws_notification(notification: dict, user_pk: int, _channel_layer):
    print("send notification message")
    await _channel_layer.group_send(
        "user_%s" % user_pk,
        {
            "type": "user_notification",
            "message": notification,
        },
    )


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
        "Authorization": f"key={FCM_TOKEN}",
    }

    async with AsyncClient() as client:
        try:
            await client.post(url, headers=headers, json=payload)
        except HTTPError:
            pass
