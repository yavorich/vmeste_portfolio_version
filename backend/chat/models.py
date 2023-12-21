from django.db import models


from django.utils.translation import gettext_lazy as _
from api.models import Event, User


class Chat(models.Model):
    event = models.OneToOneField(
        Event,
        verbose_name="Событие",
        related_name="chat",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self) -> str:
        return self.event.title


class Message(models.Model):
    chat = models.ForeignKey(
        verbose_name=_("Чат"),
        to=Chat,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
    )
    sender = models.ForeignKey(
        verbose_name=_("Отправитель"),
        to=User,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    text = models.TextField(_("Текст"))
    sent_at = models.DateTimeField(_("Время отправки"), auto_now_add=True)
    is_info = models.BooleanField()
    is_incoming = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        get_latest_by = "sent_at"


class ReadMessage(models.Model):
    message = models.ForeignKey(Message, related_name="read", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="read", on_delete=models.CASCADE)
