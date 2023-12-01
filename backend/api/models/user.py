from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from ..enums import Gender


class User(AbstractUser):
    gender = models.CharField(_("Пол"), choices=Gender.choices, max_length=6)
