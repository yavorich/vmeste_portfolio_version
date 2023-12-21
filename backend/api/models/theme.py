from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.Model):
    title = models.CharField(_("Название"), max_length=255)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self) -> str:
        return self.title
