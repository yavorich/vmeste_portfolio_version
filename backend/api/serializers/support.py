from rest_framework import serializers

from api.models import SupportRequestTheme, SupportRequestMessage


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

    def create(self, validated_data):
        validated_data["author"] = self.context.get("user")
        validated_data["event"] = self.context.get("event")
        validated_data["profile"] = self.context.get("profile")
        return super().create(validated_data)
