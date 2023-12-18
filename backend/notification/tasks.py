from asgiref.sync import async_to_sync

from config.celery import celery_app
from notification.models import PushToken
from notification.utils import send_fcm_push


@celery_app.task
def send_push_notifications_task(title, body):
    async_to_sync(send_push_notifications)(title, body)
    return "Success send push notifications"


async def send_push_notifications(title, body):
    async for push_token in PushToken.objects.filter(user__settings__sending_push=True):
        await send_fcm_push(push_token.token, title, body)

    # async for push_token in PushToken.objects.filter(device_os=PushToken.DeviceOS.IOS):
        # await send_apn_push(push_token.token, text)
