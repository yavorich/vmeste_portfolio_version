from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event
from .user import User


class SupportRequestType(models.TextChoices):
    COMPLAINT = "complaint", "Жалоба"
    HELP = "help", "Помощь"


class SupportRequestTheme(models.Model):
    name = models.CharField(_("Название темы"), max_length=31, unique=True)
    type = models.CharField(_("Тип обращения"), choices=SupportRequestType.choices)

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

    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        related_name="created_support_requests",
        on_delete=models.CASCADE,
    )
    status = models.CharField(_("Статус"), choices=Status.choices, default=Status.NEW)
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
    text = models.TextField(_("Текст"), max_length=500)

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        history_fields = {"theme": "Тема", "author_user": "Автор"}

    def __str__(self):
        return self.theme.get_type_display()

    @property
    def author_user(self):
        return (
            f"{self.author.pk}. "
            + f"{self.author.get_full_name()} {self.author.phone_number}".lstrip()
        )


class SupportAnswer(models.Model):
    support = models.OneToOneField(
        SupportRequestMessage, on_delete=models.CASCADE, related_name="answer"
    )

    text = models.TextField(_("Текст"))
    sent = models.BooleanField("Отправлен", default=False)

    class Meta:
        verbose_name = "Ответ на обращение"
        verbose_name_plural = "Ответы на обращения"

    def __str__(self):
        return self.text
