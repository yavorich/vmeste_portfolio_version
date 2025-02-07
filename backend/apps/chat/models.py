from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.api.models import Event, User
from core.utils.short_text import short_text


class Chat(models.Model):
    event = models.OneToOneField(
        Event,
        primary_key=True,
        verbose_name="Событие",
        related_name="chat",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        history_fields = {"organizer_user": "Организатор"}

    def __str__(self) -> str:
        return self.event.title

    @property
    def organizer_user(self):
        organizer = self.event.organizer
        if organizer is None:
            return "-"

        return (
            f"{organizer.pk}. "
            + f"{organizer.get_full_name()} {organizer.phone_number}".lstrip()
        )


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
    text = models.CharField(_("Текст"), max_length=300)
    sent_at = models.DateTimeField(_("Время отправки"), auto_now_add=True)
    is_info = models.BooleanField(_("Информационное"), default=False)
    is_incoming = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        get_latest_by = "sent_at"
        ordering = ["sent_at"]
        history_fields = {"sender_user": "Отправитель", "event_str": "Событие"}

    def __str__(self):
        return short_text(self.text, 50)

    @property
    def event_str(self):
        event = self.chat.event
        if event is None:
            return "-"
        return f"{event.pk}. {event.title}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        _, created = ReadMessage.objects.get_or_create(message=self, user=self.sender)
        if created:
            from apps.chat.utils import send_ws_unread_messages

            send_ws_unread_messages(self.sender)

    def is_read_by(self, user):
        return ReadMessage.objects.filter(message=self, user=user).exists()

    @property
    def sender_user(self):
        return (
            f"{self.sender.pk}. "
            + f"{self.sender.get_full_name()} {self.sender.phone_number}".lstrip()
        )


class ReadMessage(models.Model):
    message = models.ForeignKey(Message, related_name="read", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="read", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("message", "user")
