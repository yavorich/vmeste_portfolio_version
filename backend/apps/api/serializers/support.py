from rest_framework import serializers

from apps.admin_history.models import ActionFlag, HistoryLog
from apps.api.models import SupportRequestTheme, SupportRequestMessage


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
        user = self.context["user"]
        validated_data["author"] = user
        validated_data["event"] = self.context.get("event")
        validated_data["profile"] = self.context.get("profile")
        instance = super().create(validated_data)
        HistoryLog.objects.log_actions(
            user_id=user.pk,
            queryset=[instance],
            action_flag=ActionFlag.ADDITION,
            change_message=[{"added": {}}],
            is_admin=False,
        )
        return instance
