from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .event import Event
from .user import User


class SupportRequestTheme(models.Model):
    name = models.CharField(_("Название темы"), max_length=31, unique=True)

    class Meta:
        verbose_name = "Тема обращения"
        verbose_name_plural = "Темы обращений"

    def __str__(self) -> str:
        return self.name


class SupportRequestMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новое"
        IN_PROCESS = "in_process", "На рассмотрении"
        REVIEWED = "reviewed", "Рассмотрено"

    class Subject(models.TextChoices):
        PROFILE = "profile", "Пользователь"
        EVENT = "event", "Мероприятие"

    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        related_name="created_support_requests",
        on_delete=models.CASCADE,
    )
    status = models.CharField(_("Статус"), choices=Status.choices)
    subject = models.CharField(_("Тип объекта"), choices=Subject.choices)
    theme = models.ForeignKey(
        verbose_name=_("Тема"),
        to=SupportRequestTheme,
        on_delete=models.CASCADE,
        related_name="request_messages",
    )
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="support_requests",
        null=True,
    )
    profile = models.ForeignKey(
        verbose_name=_("Профиль"),
        to=User,
        on_delete=models.CASCADE,
        related_name="support_requests",
        null=True,
    )
    text = models.TextField(max_length=500)

    def clean(self) -> None:
        if not self.event and not self.profile:
            raise ValidationError(
                "Минимум одно из полей 'user' или 'event' должно быть заполнено."
            )

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
