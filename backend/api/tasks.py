from celery import shared_task
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from asgiref.sync import async_to_sync
from api.services import send_fcm_push
from api.models import PushToken


@shared_task
def send_mail_confirmation_code(email, code):
    msg_data = {
        "subject": "VMESTE - Подтверждение электронной почты",
        "from_email": EMAIL_HOST_USER,
        "recipient_list": [email],
        "message": code,
    }

    return send_mail(**msg_data)


@shared_task
def send_push_notifications_task(pk, _type):
    title = ""
    body = ""
    async_to_sync(send_push_notifications)(title, body)
    return "Success send push notifications"


async def send_push_notifications(title, body):
    async for push_token in PushToken.objects.filter(user__settings__sending_push=True):
        await send_fcm_push(push_token.token, title, body)
