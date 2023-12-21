from rest_framework import serializers
from django.db.models import Q

from api.models import Event, User
from chat.models import Message, ReadMessage
from core.utils import convert_file_to_base64


class ChatListSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source="location.address")
    location_name = serializers.CharField(source="location.name")
    unread_messages = serializers.SerializerMethodField()

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
        ]

    def get_unread_messages(self, obj: Event):
        user = self.context["user"]
        unread_messages = obj.messages.filter(~Q(read__user=user))
        return unread_messages.count()


class ChatEventSerializer(serializers.ModelSerializer):
    total_will_come = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "total_will_come",
            "title",
            "cover",
        ]

    def get_total_will_come(self, obj: Event):
        return obj.participants.count()


class SenderSerializer(serializers.ModelSerializer):
    name_and_surname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "name_and_surname",
        ]

    def get_name_and_surname(self, obj: User):
        return obj.get_full_name()

    def get_avatar(self, obj: User):
        return convert_file_to_base64(obj.avatar)


class MessageSerializer(serializers.ModelSerializer):
    sender = SenderSerializer()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "text",
            "sent_at",
            "is_info",
            "is_incoming",
            "is_mine",
        ]

    def get_is_mine(self, obj: Message):
        return self.context["user"] == obj.sender

    def to_representation(self, instance: Message):
        ReadMessage.objects.create(message=instance, user=self.context["user"])
        return super().to_representation(instance)


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
