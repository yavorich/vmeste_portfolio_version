from rest_framework import serializers

from api.models import Event, User
from chat.models import Message


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
        last_time = obj.participants.get(user=user).last_time_viewed_chat
        unread_messages = obj.messages.filter(sent_at__gt=last_time)
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
        pass


class SenderSerializer(serializers.ModelSerializer):
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
    sender = SenderSerializer()

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "text",
            "sent_at",
            "is_info",
            "is_incoming",
        ]


class MessageSendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "id",
            "text",
        ]

    def create(self, validated_data):
        for key in ["sender", "event", "is_info", "is_incoming"]:
            validated_data[key] = self.context.get(key)
        return super().create(validated_data)
