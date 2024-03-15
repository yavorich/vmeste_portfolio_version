from httpx import AsyncClient, HTTPError
from config.settings import FCM_TOKEN


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
