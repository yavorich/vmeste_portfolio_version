from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import ModelSerializer

from api.models import Notification, Event


class NotificationEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "cover"]


class NotificationListSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = Notification
        fields = ["id", "read", "created_at", "event", "text"]


class NotificationBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
        model = Notification
        fields = ["id"]

    def update(self, instance, validated_data):
        validated_data["read"] = True
        return super().update(instance, validated_data)
