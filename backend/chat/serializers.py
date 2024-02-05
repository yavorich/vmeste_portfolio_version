from rest_framework import serializers
from django.db.models import Q

from api.models import Event, User
from chat.models import Message, ReadMessage


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
        unread_messages = obj.chat.messages.filter(~Q(read__user=user))
        return unread_messages.count()


class ChatEventSerializer(serializers.ModelSerializer):
    total_will_come = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "total_will_come",
            "title",
            "cover",
        ]

    def get_total_will_come(self, obj: Event):
        return obj.participants.count()


class SenderSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
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

    def get_avatar(self, obj: User):
        headers = self.context["headers"]
        url = obj.avatar.url
        if b"host" in headers:
            host = headers[b"host"].decode()
            avatar = f"http://{host}{obj.avatar.url}"
            return avatar
        return url


class MessageSerializer(serializers.ModelSerializer):
    sender = SenderSerializer()
    is_mine = serializers.SerializerMethodField()
    sent_at_time = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "chat",
            "sender",
            "text",
            "sent_at_time",
            "is_info",
            "is_incoming",
            "is_mine",
        ]

    def get_is_mine(self, obj: Message):
        return self.context["user"] == obj.sender

    def get_sent_at_time(self, obj: Message):
        return obj.sent_at.time().strftime("%H:%M")


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

    def to_representation(self, instance):
        ReadMessage.objects.get_or_create(message=instance, user=self.context["sender"])
        return super().to_representation(instance)
