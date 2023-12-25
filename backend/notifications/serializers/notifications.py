from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import ModelSerializer, DateTimeField

from api.models import Event
from notifications.models import Notification, UserNotification


class NotificationEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "cover"]


class NotificationSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = Notification
        fields = ["id", "created_at", "event", "text"]


class UserNotificationListSerializer(ModelSerializer):
    created_at = DateTimeField(source="notification.created_at")
    event = NotificationEventSerializer(source="notification.event")

    class Meta:
        model = UserNotification
        fields = ["id", "read", "created_at", "event", "text"]


class UserNotificationBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
        model = UserNotification
        fields = ["id"]

    def update(self, instance, validated_data):
        validated_data["read"] = True
        return super().update(instance, validated_data)
