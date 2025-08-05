import json
import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models

from apps.api.models.user import User


def get_upload_path(instance, filename):
    return os.path.join("participants", str(instance.pk), "qrcode", filename)


class EventParticipant(models.Model):
    event = models.ForeignKey(
        "Event", related_name="participants", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    has_confirmed = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    kicked_by_organizer = models.BooleanField(default=False)
    chat_notifications = models.BooleanField(default=True)
    payed = models.PositiveIntegerField("Оплачено", default=0)
    qr_code = models.ImageField("QR-код", upload_to=get_upload_path, blank=True, null=True)
    qr_code_verified = models.BooleanField("QR-код отсканирован", default=False)

    class Meta:
        verbose_name = "Участник события"
        verbose_name_plural = "Участники события"
        unique_together = ("event", "user")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.qr_code:
            data = {
                "ticket_id": self.pk,
            }
            qr = qrcode.make(json.dumps(data))
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            filename = f"qr_{self.pk}.png"
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
            self.save(update_fields=["qr_code"])
