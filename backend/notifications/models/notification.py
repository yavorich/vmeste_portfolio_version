from django.db import models
from django.utils.translation import gettext_lazy as _
from api.models import User, Event


class Notification(models.Model):
    class Type(models.TextChoices):
        EVENT_REMIND = "EVENT_REMIND", "Напоминание о событии"
        EVENT_CANCELED = "EVENT_CANCELED", "Событие отменено"
        EVENT_CHANGED = "EVENT_CHANGED", "Событие изменено"
        EVENT_REC = "EVENT_REC", "Рекомендованное событие"
        ADMIN = "ADMIN", "От администрации"

    type = models.CharField(_("Тип"), choices=Type.choices)
    created_at = models.DateTimeField(_("Время создания"), auto_now_add=True)
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    title = models.CharField(_("Заголовок"), max_length=50, null=True)
    body = models.TextField(_("Текст"), max_length=500, null=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def save(self, *args, **kwargs):
        if self.title is None:
            self.title = self.event.title
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class UserNotification(models.Model):
    notification = models.ForeignKey(
        Notification,
        verbose_name="Уведомление",
        related_name="receivers",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    body = models.TextField(_("Текст"), max_length=500)
    read = models.BooleanField(_("Прочитано"), default=False)

    @property
    def short_text(self):
        max_length = 50
        if len(self.title) <= max_length:
            return self.title
        else:
            return f"{self.title[:max_length-3]}..."

    def __str__(self) -> str:
        return f"{self.notification.title}: для {self.user.get_full_name()}"
