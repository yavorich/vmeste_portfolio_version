from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .event import Event
from .user import User


class SupportTheme(models.Model):
    theme = models.CharField(max_length=31)


class SupportMessage(models.Model):
    is_event = models.BooleanField()
    theme = models.ForeignKey(
        verbose_name=_("Тема"),
        to=SupportTheme,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
    )
    profile = models.ForeignKey(
        verbose_name=_("Профиль"),
        to=User,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
    )
    text = models.TextField(max_length=500)

    def clean(self) -> None:
        if not self.event and not self.user:
            raise ValidationError(
                "Минимум одно из полей 'user' или 'event' должно быть заполнено."
            )
