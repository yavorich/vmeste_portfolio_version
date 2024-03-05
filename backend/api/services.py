import random
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.models import Event
from api.tasks import send_mail_confirmation_code
from config.settings import DEBUG


def generate_confirmation_code():
    return "".join([str(random.randint(0, 9)) for _ in range(5)])


def send_confirmation_code(user, confirm_type):
    if confirm_type == "mail" and not DEBUG:
        send_mail_confirmation_code.delay(user.email, user.confirmation_code)
    elif confirm_type == "phone" and not DEBUG:
        pass  # нужен смс-сервис


def get_event_object(id):
    if id.isdigit():
        event = get_object_or_404(Event, id=id)
        if event.is_close_event:
            raise PermissionDenied("Закрытые события доступны только по uuid")
        if not event.is_active:
            raise ValidationError({"error": "Событие заблокировано администрацией"})
        return event

    return get_object_or_404(Event, uuid=id)
