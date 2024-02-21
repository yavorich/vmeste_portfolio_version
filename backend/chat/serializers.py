from rest_framework import serializers
from rest_framework.settings import api_settings
from django.db.models import Q
from django.utils.timezone import localtime

from api.models import Event, User
from chat.models import Message


class ChatListSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source="location.address", allow_null=True)
    location_name = serializers.CharField(source="location.name", allow_null=True)
    unread_messages = serializers.SerializerMethodField()
    am_i_organizer = serializers.SerializerMethodField()

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
        ]

    def get_unread_messages(self, obj: Event):
        user = self.context["user"]
        unread_messages = obj.chat.messages.filter(~Q(read__user=user))
        return unread_messages.count()

    def get_am_i_organizer(self, obj: Event):
        organizer = obj.participants.get(is_organizer=True).user
        return organizer == self.context["user"]


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

    def get_total_will_come(self, obj: Event):
        return obj.participants.count()

    def get_am_i_organizer(self, obj: Event):
        organizer = obj.participants.get(is_organizer=True).user
        return organizer == self.context["request"].user


class CustomFileField(serializers.FileField):
    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, "use_url", api_settings.UPLOADED_FILES_USE_URL)
        if use_url:
            try:
                url = value.url
            except AttributeError:
                return None
            request = self.context.get("request", None)
            if request is not None:
                return request.build_absolute_uri(url)
            headers = self.context.get("headers", None)
            if headers is not None and b"host" in headers:
                host = headers[b"host"].decode()
                return f"http://{host}{url}"
            return url

        return value.name


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
        return obj.sent_at.astimezone(tz=localtime().tzinfo).strftime("%H:%M")


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
