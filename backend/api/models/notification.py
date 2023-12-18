from django.db import models
from django.utils.translation import gettext_lazy as _
from .user import User
from .event import Event


class Notification(models.Model):
    class Type(models.TextChoices):
        EVENT_REMIND = "EVENT_REMIND", "Напоминание о событии"
        EVENT_CANCELED = "EVENT_CANCELED", "Событие отменено"
        EVENT_CHANGED = "EVENT_CHANGED", "Событие изменено"
        EVENT_REC = "EVENT_REC", "Рекомендованное событие"

    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    text = models.TextField(max_length=255)
