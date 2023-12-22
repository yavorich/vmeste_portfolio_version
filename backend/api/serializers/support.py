from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import SupportRequestTheme, SupportRequestMessage


class SupportThemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestTheme
        fields = ["id", "name"]


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestMessage
        fields = ["subject", "theme", "event", "profile", "text"]
        extra_kwargs = {
            "subject": {"required": True},
            "theme": {"required": True},
            "text": {"required": True},
        }

    def validate(self, attrs):
        subjects = SupportRequestMessage.Subject
        if attrs["subject"] and not attrs.get(attrs["subject"]):
            raise ValidationError(
                f"{attrs['subject']}, к которому относится жалоба, не указан"
            )
        for choice in subjects:
            if attrs["subject"] != choice and attrs.get(choice) is not None:
                raise ValidationError(f"Указан лишний параметр: {choice}")

        if attrs.get("profile") == self.context["user"]:
            raise ValidationError("Вы не можете пожаловаться на свой профиль")

        if event := attrs.get("event"):
            if event.organizer == self.context["user"]:
                raise ValidationError(
                    "Вы не можете пожаловаться на событие, которое организуете"
                )
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["author"] = self.context.get("user")
        validated_data["status"] = SupportRequestMessage.Status.NEW
        return super().create(validated_data)
