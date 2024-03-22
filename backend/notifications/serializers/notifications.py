from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from django.utils.timezone import localtime, timedelta

from api.models import Event
from core.serializers import CustomFileField
from notifications.models import GroupNotification, UserNotification


class NotificationEventSerializer(ModelSerializer):
    cover = CustomFileField()

    class Meta:
        model = Event
        fields = ["id", "title", "cover"]


class NotificationSerializer(ModelSerializer):
    event = NotificationEventSerializer()

    class Meta:
        model = GroupNotification
        fields = ["id", "created_at", "event", "title", "body"]


class UserNotificationSerializer(ModelSerializer):
    event = NotificationEventSerializer()
    date = SerializerMethodField()
    time = SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = ["id", "read", "date", "time", "event", "title", "body"]

    def get_date(self, obj: UserNotification):
        date = obj.created_at.astimezone(tz=localtime().tzinfo).date()
        if localtime().date() == date:
            return "Сегодня"
        elif localtime().date() == date + timedelta(days=1):
            return "Вчера"
        else:
            return date.strftime("%d.%m.%Y")

    def get_time(self, obj: UserNotification):
        return obj.created_at.astimezone(tz=localtime().tzinfo).strftime("%H:%M")


class UserNotificationBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
        model = UserNotification
        fields = ["id"]

    def update(self, instance, validated_data):
        validated_data["read"] = True
        return super().update(instance, validated_data)


class UserNotificationMessageSerializer(ModelSerializer):
    notification = SerializerMethodField()
    unread = SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = ["notification", "unread"]

    def get_notification(self, obj: UserNotification):
        return UserNotificationSerializer(instance=obj).data

    def get_unread(self, obj: UserNotification):
        return obj.user.notifications.filter(read=False).count()
