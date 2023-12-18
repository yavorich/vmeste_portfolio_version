from django.db.models import Model, CharField, TextChoices, ForeignKey, CASCADE
from django.contrib.auth import get_user_model


User = get_user_model()


class PushToken(Model):
    class DeviceOS(TextChoices):
        ANDROID = "android"
        IOS = "ios"

    user = ForeignKey(User, on_delete=CASCADE, related_name="push_tokens")
    token = CharField("Токен", max_length=256)
    device_os = CharField(
        "Операционная система", max_length=8, choices=DeviceOS.choices
    )

    def __str__(self):
        return ""

    class Meta:
        verbose_name_plural = "Пуш-токены"
        verbose_name = "токен"
