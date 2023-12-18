from httpx import AsyncClient, HTTPError

from config.settings import FCM_TOKEN  # , APN_TOKEN, APNS_TOPIC


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


async def send_apn_push(token, data):
    payload = {
        "aps": {"alert": "Звонит Анатолий Чакарь"},
        "id": "44d915e1-5ff4-4bed-bf13-c423048ec97a",
        "nameCaller": "Анатолий Чакарь",
        "handle": "0123456789",
        "isVideo": False,
        "isAutdio": True,
    }
    url = f"https://api.push.apple.com:443/3/device/{token}"
    headers = {
        # "apns-topic": APNS_TOPIC,
        "apns-push-type": "voip",
        # "Authorization": f"bearer {APN_TOKEN}",
        "apns-priority": "5",
        "Content-Type": "application/json",
    }

    async with AsyncClient() as client:
        try:
            await client.post(url, headers=headers, json=payload)
        except HTTPError:
            pass
