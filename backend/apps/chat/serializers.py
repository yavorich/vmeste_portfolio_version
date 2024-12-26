from rest_framework import serializers
from django.db.models import Q
from django.utils.timezone import localtime

from apps.api.models import Event, User
from apps.chat.models import Message
from core.serializers import CustomFileField


class ChatListSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    location_name = serializers.CharField(source="location.name", allow_null=True)
    unread_messages = serializers.SerializerMethodField()
    am_i_organizer = serializers.SerializerMethodField()
    total_will_come = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "cover",
            "day_and_time",
            "address",
            "location_name",
            "unread_messages",
            "am_i_organizer",
            "total_will_come",
        ]
        extra_kwargs = {"cover": {"source": "cover_medium"}}

    def get_address(self, obj: Event):
        address = obj.location.address
        return f"{obj.city.name}, {address}"

    def get_unread_messages(self, obj: Event):
        user = self.context["user"]
        unread_messages = obj.chat.messages.filter(~Q(read__user=user))
        return unread_messages.count()

    def get_am_i_organizer(self, obj: Event):
        organizer = obj.participants.get(is_organizer=True).user
        return organizer == self.context["user"]

    def get_total_will_come(self, obj: Event):
        return obj.participants.count()


class ChatEventSerializer(serializers.ModelSerializer):
    total_will_come = serializers.SerializerMethodField()
    am_i_organizer = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "total_will_come",
            "title",
            "cover",
            "am_i_organizer",
        ]
        extra_kwargs = {"cover": {"source": "cover_medium"}}

    def get_total_will_come(self, obj: Event):
        return obj.participants.count()

    def get_am_i_organizer(self, obj: Event):
        organizer = obj.participants.get(is_organizer=True).user
        return organizer == self.context["request"].user


class SenderSerializer(serializers.ModelSerializer):
    avatar = CustomFileField()
    name_and_surname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "name_and_surname",
        ]

    def get_name_and_surname(self, obj: User):
        return obj.get_full_name()


class MessageSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="chat.event.title")
    sender = SenderSerializer()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "chat",
            "event_name",
            "sender",
            "text",
            "sent_at",
            "is_info",
            "is_incoming",
            "is_mine",
        ]

    def get_is_mine(self, obj: Message):
        return self.context["user"] == obj.sender


class MessageSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "text",
        ]

    def create(self, validated_data):
        for key in ["sender", "chat", "is_info", "is_incoming"]:
            validated_data[key] = self.context.get(key)
        return super().create(validated_data)
