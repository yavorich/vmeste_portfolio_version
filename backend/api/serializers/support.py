from rest_framework import serializers

from api.models import SupportRequestTheme, SupportRequestMessage


class SupportThemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestTheme
        fields = ["id", "name"]


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestMessage
        fields = ["theme", "event", "profile", "text"]
        extra_kwargs = {
            "type": {"required": True},
            "theme": {"required": True},
            "text": {"required": True},
        }

    def create(self, validated_data):
        validated_data["author"] = self.context.get("user")
        return super().create(validated_data)
