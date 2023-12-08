from rest_framework import serializers
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.utils.timezone import now, datetime

from api.models import (
    Event,
    EventParticipant,
    Location,
    City,
    Country,
    Theme,
    Category,
    User,
)
from api.enums import EventState, Gender
from api.serializers import (
    LocationSerializer,
    LocationDetailSerializer,
    CategoryTitleSerializer,
)


class EventMixin:
    def get_stats(self, obj: Event, gender: Gender):
        total_field = "total_" + gender
        participants = obj.get_participants_by_gender(gender)
        total = getattr(obj, total_field)
        count = participants.filter(user__gender=gender).count()
        if total > 0:
            return f"{count}/{total}"
        return "0/0"

    def get_stats_men(self, obj: Event):
        return self.get_stats(obj, Gender.MALE)

    def get_stats_women(self, obj: Event):
        return self.get_stats(obj, Gender.FEMALE)

    def get_date(self, obj: Event):
        return {
            "date_and_year": self.get_date_and_year(obj),
            "day_and_time": self.get_day_and_time(obj),
        }

    def get_date_and_year(self, obj: Event):
        return _date(obj.date, "j E, Y")

    def get_day_and_time(self, obj: Event):
        return (
            _date(obj.date, "l")
            + _time(obj.start_time, ", H:i")
            + _time(obj.end_time, "-H:i")
        )

    def get_date_and_time(self, obj: Event):
        return _date(obj.date, "j E") + _time(obj.start_time, ", H:i")

    def get_am_i_organizer(self, obj: Event):
        return self.context.get("user") == obj.organizer

    def get_am_i_registered(self, obj: Event):
        user = self.context.get("user")
        if user is not None:
            return obj.get_participant(user=user) is not None

    def get_am_i_confirmed(self, obj: Event):
        user = self.context.get("user")
        if user is not None:
            participant = obj.get_participant(user=user)
            if participant is not None:
                return participant.has_confirmed
        return False

    def get_are_there_free_places(self, obj: Event):
        user = self.context.get("user")
        if user is not None:
            return obj.has_free_places(gender=user.gender)

    def get_participants(self, obj: Event):
        participants = obj.get_participants()
        serializer = EventParticipantSerializer(participants, many=True)
        return serializer.data

    def get_state(self, obj: Event):
        if now() < datetime.combine(obj.date, obj.start_time, tzinfo=now().tzinfo):
            return EventState.BEFORE
        if now() > datetime.combine(obj.date, obj.end_time, tzinfo=now().tzinfo):
            return EventState.AFTER
        return EventState.WHILE

    def to_representation(self, instance):
        data = super().to_representation(instance)
        auth_only_fields = [
            "am_i_organizer",
            "am_i_registered",
            "am_i_confirmed",
            "are_there_free_places",
            "did_organizer_marking",
        ]
        if not self.context.get("user"):
            for field in auth_only_fields:
                if field in data:
                    data.pop(field)
        return data


class EventParticipantSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source="user.avatar")

    class Meta:
        model = EventParticipant
        fields = ["avatar"]


# можно позже сделать как UserSerializer, если понадобится где-то еще
class EventOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]


class EventDetailSerializer(EventMixin, serializers.ModelSerializer):
    location = LocationDetailSerializer()
    stats_men = serializers.SerializerMethodField()
    stats_women = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    theme_name = serializers.CharField(source="theme.title")
    category_name = CategoryTitleSerializer(source="categories", many=True)
    state = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    organizer = EventOrganizerSerializer()
    am_i_organizer = serializers.SerializerMethodField()
    am_i_registered = serializers.SerializerMethodField()
    are_there_free_places = serializers.SerializerMethodField()
    am_i_confirmed = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "max_age",
            "min_age",
            "link",
            "participants",
            "title",
            "cover",
            "description",
            "location",
            "stats_men",
            "stats_women",
            "date",
            "theme_name",
            "category_name",
            "state",
            "organizer",
            "am_i_organizer",
            "am_i_registered",
            "are_there_free_places",
            "did_organizer_marking",
            "am_i_confirmed",
        ]


class EventSerializer(EventMixin, serializers.ModelSerializer):
    location = LocationSerializer()
    stats_men = serializers.SerializerMethodField()
    stats_women = serializers.SerializerMethodField()
    am_i_organizer = serializers.SerializerMethodField()
    date_and_time = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "max_age",
            "min_age",
            "cover",
            "short_description",
            "location",
            "stats_men",
            "stats_women",
            "date_and_time",
            "am_i_organizer",
        ]


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True
    )
    location_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "cover",
            "title",
            "country",
            "city",
            "date",
            "start_time",
            "end_time",
            "location_name",
            "address",
            "latitude",
            "longitude",
            "max_age",
            "min_age",
            "theme",
            "categories",
            "total_male",
            "total_female",
            "short_description",
            "description",
            "is_close_event",
            "is_draft",
        ]
        extra_kwargs = {f: {"required": True} for f in fields}

    def get_organizer(self):
        return self.context["user"]

    def create(self, validated_data):
        location, created = Location.objects.get_or_create(
            country=validated_data["country"],
            city=validated_data["city"],
            name=validated_data.pop("location_name"),
            address=validated_data.pop("address"),
            defaults={
                "latitude": validated_data.pop("latitude"),
                "longitude": validated_data.pop("longitude"),
                "status": Location.Status.UNKNOWN,
            },
        )

        validated_data["location"] = location
        validated_data["organizer"] = self.context["user"]
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {"id": data["id"]}
