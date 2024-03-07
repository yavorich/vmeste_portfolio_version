import os
import random
from moviepy.editor import VideoFileClip
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.models import Event, EventMedia
from api.tasks import send_mail_confirmation_code
from config.settings import DEBUG, MEDIA_ROOT


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


def generate_video_preview(instance: EventMedia):
    clip = VideoFileClip(instance.file.path)
    preview_dir = os.path.join(MEDIA_ROOT, "previews")
    if not os.path.exists(preview_dir):
        os.mkdir(preview_dir)
    preview_filename = instance.file.name.split("/")[-1] + "_preview.png"
    preview_path = os.path.join(preview_dir, preview_filename)
    clip.save_frame(
        preview_path, t=clip.duration / 2
    )  # Генерация превью из середины видео
    return os.path.join("previews", preview_filename)
