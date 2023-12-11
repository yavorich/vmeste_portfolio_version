from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import SupportTheme, SupportMessage


class SupportThemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTheme
        fields = ["id", "theme"]


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["is_event", "theme", "event", "profile", "text"]
        extra_kwargs = {
            "is_event": {"required": True},
            "theme": {"required": True},
            "text": {"required": True},
        }

    def validate(self, attrs):
        if attrs["is_event"] and not attrs.get("event"):
            raise ValidationError("Событие, к которому относится жалоба, не указано")
        if not attrs["is_event"] and not attrs.get("profile"):
            raise ValidationError("Профиль, к которому относится жалоба, не указан")
        if attrs["is_event"] and attrs.get("profile"):
            raise ValidationError("Указание профиля в жалобе на событие не требуется")
        if not attrs["is_event"] and attrs.get("event"):
            raise ValidationError("Указание события в жалобе на профиль не требуется")
        if attrs.get("profile") == self.context["user"]:
            raise ValidationError("Вы не можете пожаловаться на свой профиль")
        if event := attrs.get("event"):
            if event.organizer == self.context["user"]:
                raise ValidationError(
                    "Вы не можете пожаловаться на событие, которое организуете"
                )
        return super().validate(attrs)
