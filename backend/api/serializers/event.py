from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer
from django.utils.timezone import now, datetime
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

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
from api.enums import EventState
from api.serializers import (
    LocationSerializer,
    CategoryTitleSerializer,
    ThemeSerializer,
)
from api.documents import EventDocument
from core.utils import convert_file_to_base64, validate_file_size
from core.serializers import CustomFileField


class EventMixin:
    def get_date(self, obj: Event):
        return {
            "date_and_year": obj.date_and_year,
            "day_and_time": obj.day_and_time,
        }

    def get_am_i_organizer(self, obj: Event):
        user = self.context.get("user")
        if user is not None:
            return self.context.get("user").id == obj.organizer.id

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
            return obj.get_free_places(gender=user.gender) > 0

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


class EventParticipantSerializer(ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = EventParticipant
        fields = ["avatar"]

    def get_avatar(self, obj: EventParticipant):
        return convert_file_to_base64(obj.user.avatar)


# можно позже сделать как UserSerializer, если понадобится где-то еще
class EventOrganizerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]


class EventDetailSerializer(EventMixin, ModelSerializer):
    location = LocationSerializer()
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
    cover = serializers.SerializerMethodField()

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

    def get_cover(self, obj: Event):
        return convert_file_to_base64(obj.cover.file)


class EventDocumentSerializer(EventMixin, DocumentSerializer):
    am_i_organizer = serializers.SerializerMethodField()
    stats_men = serializers.CharField(source="participants.stats.men")
    stats_women = serializers.CharField(source="participants.stats.women")

    class Meta:
        document = EventDocument
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
    cover = CustomFileField(validators=[validate_file_size])

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

    def prepare_location(self, validated_data):
        location, created = Location.objects.get_or_create(
            country=validated_data["country"],
            city=validated_data["city"],
            name=validated_data.pop("location_name"),
            address=validated_data.pop("address"),
            defaults={
                "latitude": validated_data.pop("latitude"),
                "longitude": validated_data.pop("longitude"),
                "status": Location.Status.UNKNOWN,
                "cover": validated_data["cover"],
            },
        )

        validated_data["location"] = location
        validated_data["organizer"] = self.context["user"]
        return validated_data

    def create(self, validated_data):
        validated_data = self.prepare_location(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.prepare_location(validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        instance.link = instance.get_absolute_url()
        instance.save()
        data = super().to_representation(instance)
        return {"id": data["id"]}


class FilterQuerySerializer(Serializer):
    date = serializers.DateField(required=False)
    max_age = serializers.IntegerField(required=False)
    min_age = serializers.IntegerField(required=False)
    city = serializers.IntegerField(required=False, read_only=True)
    country = serializers.IntegerField(required=False, read_only=True)
    category = serializers.ListField(child=serializers.IntegerField(), required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not (categories := data.get("category")):
            return data
        filtered_themes = Theme.objects.filter(categories__id__in=categories).distinct()
        data["themes"] = ThemeSerializer(
            filtered_themes, many=True, context={"categories": categories}
        ).data
        data.pop("category")
        return data
