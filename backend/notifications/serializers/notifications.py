from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    SerializerMethodField,
)

from api.models import Event
from notifications.models import Notification, UserNotification
from core.utils import convert_file_to_base64


class NotificationEventSerializer(ModelSerializer):
    cover = SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "title", "cover"]

    def get_cover(self, obj: Event):
        return convert_file_to_base64(obj.cover.file)


class NotificationSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = Notification
        fields = ["id", "created_at", "event", "title", "body"]


class UserNotificationListSerializer(ModelSerializer):
    created_at = DateTimeField(source="notification.created_at")
    event = NotificationEventSerializer(source="notification.event")

    class Meta:
        model = UserNotification
        fields = ["id", "read", "created_at", "event", "body"]


class UserNotificationBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
        model = UserNotification
        fields = ["id"]

    def update(self, instance, validated_data):
        validated_data["read"] = True
        return super().update(instance, validated_data)
