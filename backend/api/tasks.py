from celery import shared_task
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER


@shared_task
def send_mail_confirmation_code(email, code):
    msg_data = {
        "subject": "VMESTE - Подтверждение электронной почты",
        "from_email": EMAIL_HOST_USER,
        "recipient_list": [email],
        "message": code
    }

    return send_mail(**msg_data)
