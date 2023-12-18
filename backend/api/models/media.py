from django.db import models
from django.utils.translation import gettext_lazy as _
import os


def get_upload_path(instance, filename):
    return os.path.join("images", str(instance.pk), filename)


class EventMedia(models.Model):
    class MediaType(models.TextChoices):
        PHOTO = "photo", "Фото"
        VIDEO = "video", "Видео"

    file_type = models.CharField(_("Тип файла"), choices=MediaType.choices)
    file = models.FileField(upload_to=get_upload_path)
    file_name = models.CharField(_("Имя файла"))
    weight = models.FloatField()
    duration = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
