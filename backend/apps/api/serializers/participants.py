from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin

from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time

from apps.api.models import Event, EventParticipant
from apps.api.serializers import LocationSerializer
from apps.api.enums import Gender


class EventMarkingSerializer(ModelSerializer):
    location = LocationSerializer(remove_fields=["city", "country"])
    date_and_year = serializers.SerializerMethodField()
    day_and_time = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "date_and_year",
            "day_and_time",
            "location",
        ]

    def get_date_and_year(self, obj: Event):
        return _date(obj.date, "j E, Y")

    def get_day_and_time(self, obj: Event):
        return (
            _date(obj.date, "l")
            + _time(obj.start_time, ", H:i")
            + _time(obj.end_time, "-H:i")
        )


class EventTitleSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title"]


class EventParticipantUserSerializer(ModelSerializer):
    profile_id = serializers.IntegerField(source="user.id")
    avatar = serializers.FileField(source="user.avatar")
    name_and_surname = serializers.SerializerMethodField()

    class Meta:
        model = EventParticipant
        fields = [
            "id",
            "profile_id",
            "name_and_surname",
            "avatar",
            "has_confirmed",
            "is_organizer",
        ]

    def get_name_and_surname(self, obj: EventParticipant):
        return obj.user.get_full_name()


class EventParticipantsListSerializer(ModelSerializer):
    event = serializers.SerializerMethodField()
    amount_men = serializers.SerializerMethodField()
    amount_women = serializers.SerializerMethodField()
    men = serializers.SerializerMethodField()
    women = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "event",
            "amount_men",
            "amount_women",
            "men",
            "women",
            "organizer",
        ]

    def get_amount_men(self, obj: Event):
        return self.get_amount(obj, gender=Gender.MALE)

    def get_amount_women(self, obj: Event):
        return self.get_amount(obj, gender=Gender.FEMALE)

    def get_amount(self, obj: Event, gender: Gender):
        total = getattr(obj, "total_" + gender)
        will_come = obj.participants.filter(user__gender=gender).count()
        return {"total": total, "will_come": will_come}

    def get_men(self, obj: Event):
        men = obj.participants.filter(user__gender=Gender.MALE)
        serializer = EventParticipantUserSerializer(
            men, many=True, context=self.context
        )
        return serializer.data

    def get_women(self, obj: Event):
        women = obj.participants.filter(user__gender=Gender.FEMALE)
        serializer = EventParticipantUserSerializer(
            women, many=True, context=self.context
        )
        return serializer.data

    def get_organizer(self, obj: Event):
        organizer = obj.participants.get(is_organizer=True)
        serializer = EventParticipantUserSerializer(
            organizer, many=False, context=self.context
        )
        return serializer.data

    def get_event(self, obj: Event):
        serializer = EventTitleSerializer(obj)
        return serializer.data


class EventParticipantBulkListSerializer(BulkListSerializer):
    pass


class EventParticipantBulkSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = EventParticipant
        list_serializer_class = EventParticipantBulkListSerializer
        fields = ["id", "has_confirmed"]

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class EventParticipantDeleteSerializer(ModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ["id"]
