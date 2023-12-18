from django.db import models
from django.utils.translation import gettext_lazy as _
import os

from api.models import Event


def get_upload_path(instance, filename):
    return os.path.join("images", str(instance.event.id), filename)


class EventMedia(models.Model):
    class FileType(models.TextChoices):
        PHOTO = "photo", "Фото"
        VIDEO = "video", "Видео"

    event = models.ForeignKey(Event, related_name="media", on_delete=models.CASCADE)
    file_type = models.CharField(_("Тип файла"), choices=FileType.choices)
    file = models.FileField(upload_to=get_upload_path)
    file_name = models.CharField(_("Имя файла"))
    weight = models.FloatField()
    duration = models.FloatField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
