from django.db import models
from django.utils.translation import gettext_lazy as _
import os

from api.models import Event, User


def get_upload_path(instance, filename):
    return os.path.join("event", "uploaded", str(instance.event.id), filename)


class EventMedia(models.Model):
    class FileType(models.TextChoices):
        PHOTO = "photo", "Фото"
        VIDEO = "video", "Видео"

    event = models.ForeignKey(Event, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(_("Файл"), upload_to=get_upload_path)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)
    author = models.ForeignKey(
        User, verbose_name=_("Автор"), related_name="media", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Медиафайл"
        verbose_name_plural = "Медиафайлы"
