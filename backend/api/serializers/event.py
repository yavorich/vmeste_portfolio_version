from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField,
    IntegerField,
)
from django.template.defaultfilters import date as _date
from django.utils.timezone import now
from ..models import Event, EventParticipant
from ..enums import Gender, EventState
from .location import LocationSerializer, LocationDetailSerializer


class EventMixin:
    def get_stats(self, obj: Event, gender: Gender):
        participants = obj.get_participants()
        total = participants.count()
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
        return _date(obj.start_datetime, "j E, Y")

    def get_day_and_time(self, obj: Event):
        return _date(obj.start_datetime, "l, H:i")

    def get_date_and_time(self, obj: Event):
        return _date(obj.start_datetime, "j E, H:i") + _date(obj.end_datetime, "-H:i")

    def get_am_i_organizer(self, obj: Event):
        user = self.context.get("user")
        organizer = obj.get_organizer()
        return user == organizer

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
        return obj.has_free_places()

    def get_organizer(self, obj: Event):
        organizer = obj.get_organizer()
        serializer = EventOrganizerSerializer(organizer)
        return serializer.data

    def get_participants(self, obj: Event):
        participants = obj.get_participants()
        serializer = EventParticipantSerializer(participants, many=True)
        return serializer.data

    def get_state(self, obj: Event):
        if now() < obj.start_datetime:
            return EventState.BEFORE
        if now() > obj.end_datetime:
            return EventState.AFTER
        return EventState.WHILE

    def get_short_description(self, obj: Event):
        return obj.description.split(".")[0]  # what if sentence is too long?

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


class EventParticipantSerializer(ModelSerializer):
    avatar = CharField(source="user.avatar")

    class Meta:
        model = EventParticipant
        fields = ["avatar"]


class EventOrganizerSerializer(ModelSerializer):
    id = IntegerField(source="user.id")
    first_name = CharField(source="user.first_name")
    last_name = CharField(source="user.last_name")

    class Meta:
        model = EventParticipant
        fields = ["id", "first_name", "last_name"]


class EventDetailSerializer(EventMixin, ModelSerializer):
    location = LocationDetailSerializer()
    stats_men = SerializerMethodField()
    stats_women = SerializerMethodField()
    date = SerializerMethodField()
    theme_name = CharField(source="theme.title")
    category_name = CharField(source="category.title")
    state = SerializerMethodField()
    participants = SerializerMethodField()
    organizer = SerializerMethodField()
    am_i_organizer = SerializerMethodField()
    am_i_registered = SerializerMethodField()
    are_there_free_places = SerializerMethodField()
    am_i_confirmed = SerializerMethodField()

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


class EventSerializer(EventMixin, ModelSerializer):
    location = LocationSerializer()
    stats_men = SerializerMethodField()
    stats_women = SerializerMethodField()
    am_i_organizer = SerializerMethodField()
    date_and_time = SerializerMethodField()
    short_description = SerializerMethodField()

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
