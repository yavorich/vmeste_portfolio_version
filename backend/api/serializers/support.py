from rest_framework import serializers
from rest_framework.serializers import ValidationError

from api.models import SupportRequestTheme, SupportRequestMessage, SupportRequestType


class SupportThemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestTheme
        fields = ["id", "name"]


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestMessage
        fields = ["theme", "text"]
        extra_kwargs = {
            "theme": {"required": True},
            "text": {"required": True},
        }

    # def validate(self, attrs):
    #     theme = attrs["theme"]
    #     event = attrs.get("event")
    #     profile = attrs.get("profile")
    #     user = self.context["user"]

    #     if theme.type == SupportRequestType.COMPLAINT:
    #         if event and profile or not event and not profile:
    #             raise ValidationError(
    #                 "Должен быть указан ровно один из параметров: 'event', 'profile'"
    #             )
    #         if event and event.participants.get(is_organizer=True).user == user:
    #             raise ValidationError(
    #                 "Вы не можете пожаловаться на организуемое вами событие"
    #             )
    #         if profile and profile == user:
    #             raise ValidationError("Вы не можете пожаловаться на свой профиль")
    #     if theme.type == SupportRequestType.HELP:
    #         for key in ["event", "profile"]:
    #             if key in attrs:
    #                 raise ValidationError(
    #                     f"Для обращения типа 'help' указан лишний параметр: '{key}'"
    #                 )
    #     return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context.get("user")
        validated_data["event"] = self.context.get("event")
        validated_data["profile"] = self.context.get("profile")
        return super().create(validated_data)
