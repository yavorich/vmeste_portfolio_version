from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(_("Название"), max_length=255)

    class Meta:
        verbose_name_plural = "Countries"
