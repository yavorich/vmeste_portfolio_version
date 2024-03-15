from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import (
    ModelSerializer,
)

from api.models import Event
from notifications.models import GroupNotification, UserNotification


class NotificationEventSerializer(ModelSerializer):

    class Meta:
        model = Event
        fields = ["id", "title", "cover"]


class NotificationSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = GroupNotification
        fields = ["id", "created_at", "event", "title", "body"]


class UserNotificationListSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = UserNotification
        fields = ["id", "read", "created_at", "event", "title", "body"]


class UserNotificationBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
        model = UserNotification
        fields = ["id"]

    def update(self, instance, validated_data):
        validated_data["read"] = True
        return super().update(instance, validated_data)
