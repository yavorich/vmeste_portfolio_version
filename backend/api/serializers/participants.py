from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time

from api.models import Event, EventParticipant, User
from api.serializers import LocationSerializer
from api.enums import Gender


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
    name_and_surname = serializers.SerializerMethodField()
    user_confirmed = serializers.BooleanField(source="has_confirmed")

    class Meta:
        model = EventParticipant
        fields = [
            "id",
            "name_and_surname",
            "avatar",
            "user_confirmed",
        ]

    def get_name_and_surname(self, obj: EventParticipant):
        return obj.user.get_full_name()


class EventOrganizerUserSerializer(ModelSerializer):
    name_and_surname = serializers.SerializerMethodField()
    in_men = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "name_and_surname",
            "avatar",
            "in_men",
        ]

    def get_name_and_surname(self, obj: User):
        return obj.get_full_name()

    def get_in_men(self, obj: User):
        return obj.gender == Gender.MALE


class EventRetrieveParticipantsSerializer(ModelSerializer):
    event = serializers.SerializerMethodField()
    amount_men = serializers.SerializerMethodField()
    amount_women = serializers.SerializerMethodField()
    men = serializers.SerializerMethodField()
    women = serializers.SerializerMethodField()
    organizer = EventOrganizerUserSerializer()

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
        will_come = obj.participants.filter(
            user__gender=gender,
            has_confirmed=True,
        ).count()
        return {"total": total, "will_come": will_come}

    def get_men(self, obj: Event):
        men = obj.get_participants_by_gender(Gender.MALE)
        serializer = EventParticipantUserSerializer(men, many=True)
        return serializer.data

    def get_women(self, obj: Event):
        women = obj.get_participants_by_gender(Gender.FEMALE)
        serializer = EventParticipantUserSerializer(women, many=True)
        return serializer.data

    def get_event(self, obj: Event):
        serializer = EventTitleSerializer(obj)
        return serializer.data


class EventParticipantBulkListSerializer(BulkListSerializer):
    has_confirmed = serializers.SerializerMethodField(read_only=False)

    def get_has_confirmed(self, obj):
        return True


class EventParticipantBulkUpdateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = EventParticipant
        list_serializer_class = EventParticipantBulkListSerializer
        fields = [
            "id",
        ]

    def update(self, instance, validated_data):
        validated_data["has_confirmed"] = True
        return super().update(instance, validated_data)


class EventParticipantDeleteSerializer(ModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ["id"]
