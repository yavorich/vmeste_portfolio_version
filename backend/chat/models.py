from django.db import models


from django.utils.translation import gettext_lazy as _
from api.models import Event, User


class Message(models.Model):
    sender = models.ForeignKey(
        verbose_name=_("Пользователь"),
        to=User,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_info = models.BooleanField()
    is_incoming = models.BooleanField(null=True)  # join/left


class ReadMessage(models.Model):
    message = models.ForeignKey(Message, related_name="read", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="read", on_delete=models.CASCADE)
