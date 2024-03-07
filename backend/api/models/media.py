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
    mimetype = models.CharField(max_length=31, blank=True, null=True)
    preview = models.FileField(blank=True, null=True)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)
    author = models.ForeignKey(
        User, verbose_name=_("Автор"), related_name="media", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Медиафайл"
        verbose_name_plural = "Медиафайлы"

    # def generate_video_preview(self):
    #     video_path = self.file.path
    #     clip = VideoFileClip(video_path)
    #     preview_path = os.path.join(
    #         MEDIA_ROOT, "previews", self.file.name, "_preview.png"
    #     )
    #     clip.save_frame(
    #         preview_path, t=clip.duration / 2
    #     )  # Генерация превью из середины видео
    #     return preview_path

    # def save(self, *args, **kwargs):
    #     self.mimetype = mimetypes.guess_type(self.file.url)[0]
    #     if "video" in self.mimetype:
    #         self.preview = self.generate_video_preview()
    #     return super().save(*args, **kwargs)
