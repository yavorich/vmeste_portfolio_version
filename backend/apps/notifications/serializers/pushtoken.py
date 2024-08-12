from rest_framework.serializers import ModelSerializer

from apps.notifications.models import PushToken


class PushTokenSerializer(ModelSerializer):
    class Meta:
        model = PushToken
        fields = ("token", "device_os")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        instance = self.Meta.model.objects.filter(**validated_data).first()
        if instance is None:
            return self.Meta.model.objects.create(**validated_data)
        else:
            return instance
