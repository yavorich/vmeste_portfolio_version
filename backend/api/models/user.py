from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from api.enums import Gender


class User(AbstractUser):
    gender = models.CharField(_("Пол"), choices=Gender.choices, max_length=6, null=True)
    avatar = models.TextField(_("Аватар"), null=True)

    def save(self, *args, **kwargs):
        if self.password:
            self.set_password(self.password)
        super().save(*args, **kwargs)
