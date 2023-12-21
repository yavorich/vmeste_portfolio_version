from django.db import models
from django.utils.translation import gettext_lazy as _

from .theme import Theme


class Category(models.Model):
    title = models.CharField(_("Название"), max_length=255)
    theme = models.ForeignKey(
        Theme, related_name="categories", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return str(self.title)
