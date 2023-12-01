from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..enums import Gender


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    gender = models.CharField(_("Пол"), choices=Gender.choices, max_length=6)
