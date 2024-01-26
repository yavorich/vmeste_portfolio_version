from django.db import models

from api.models import User


class PushToken(models.Model):
    class DeviceOS(models.TextChoices):
        ANDROID = "android"
        IOS = "ios"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_tokens")
    token = models.CharField("Токен", max_length=256)
    device_os = models.CharField(
        "Операционная система", max_length=8, choices=DeviceOS.choices
    )

    def __str__(self):
        return ""

    class Meta:
        verbose_name_plural = "Пуш-токены"
        verbose_name = "токен"
