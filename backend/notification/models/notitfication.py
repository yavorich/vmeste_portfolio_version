from django.db.models import Model, DateTimeField, TextField, CharField
from django.utils import timezone


class Notification(Model):
    title = CharField("Заголовок", max_length=256)
    body = TextField("Тело", null=True, blank=True)
    date = DateTimeField("Дата, время", default=timezone.now)

    def __str__(self):
        return ""

    @property
    def short_text(self):
        max_length = 50
        if len(self.title) <= max_length:
            return self.title
        else:
            return f"{self.title[:max_length-3]}..."

    class Meta:
        verbose_name_plural = "Уведомления"
        verbose_name = "уведомление"
