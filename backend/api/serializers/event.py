from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer
from django.utils.timezone import localtime, datetime, timedelta
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework.exceptions import ValidationError

from api.models import (
    Event,
    EventParticipant,
    Location,
    City,
    Country,
    Theme,
    User,
)
from api.enums import EventState
from api.serializers import (
    LocationSerializer,
    CategoryTitleSerializer,
    ThemeSerializer,
)
from api.documents import EventDocument
from api.models import EventFastFilter
from core.utils import validate_file_size


class CharacterSeparatedField(serializers.ListField):
    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop("separator", ",")
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data = data.split(self.separator)
        return super().to_internal_value(data)


class EventMixin:
    def get_date(self, obj: Event):
        return {
            "date_and_year": obj.date_and_year,
            "day_and_time": obj.day_and_time,
        }

    def get_am_i_organizer(self, obj: Event):
        return self.context.get("user").id == obj.organizer.id

    def get_am_i_registered(self, obj: Event):
        user = self.context.get("user")
        participant = obj.get_participant(user=user)
        return participant is not None

    def get_am_i_confirmed(self, obj: Event):
        user = self.context.get("user")
        participant = obj.get_participant(user=user)
        return getattr(participant, "has_confirmed", False)

    def get_are_there_free_places(self, obj: Event):
        user = self.context.get("user")
        return obj.get_free_places(gender=user.gender) > 0

    def get_participants(self, obj: Event):
        participants = obj.participants.all()
        serializer = EventParticipantSerializer(
            participants, many=True, context=self.context
        )
        return serializer.data

    def get_organizer(self, obj: Event):
        serializer = EventOrganizerSerializer(obj.organizer, context=self.context)
        return serializer.data

    def get_state(self, obj: Event):
        if localtime() < obj.start_datetime:
            return EventState.BEFORE
        if localtime() > obj.end_datetime:
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
        if not self.context.get("user").is_authenticated:
            for field in auth_only_fields:
                if field in data:
                    data.pop(field)
        return data


class EventParticipantSerializer(ModelSerializer):
    avatar = serializers.FileField(source="user.avatar")

    class Meta:
        model = EventParticipant
        fields = ["avatar"]


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
    organizer = serializers.SerializerMethodField()
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


class EventDocumentSerializer(EventMixin, DocumentSerializer):
    am_i_organizer = serializers.SerializerMethodField()
    stats_men = serializers.CharField(source="participants.stats.men")
    stats_women = serializers.CharField(source="participants.stats.women")
    cover = serializers.SerializerMethodField()

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

    def get_cover(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover) if obj.cover else None


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())
    categories = serializers.ListField(child=serializers.IntegerField())
    location_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    cover = serializers.FileField(validators=[validate_file_size])

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

    def validate(self, attrs):
        if attrs["min_age"] >= attrs["max_age"]:
            raise ValidationError(
                "Минимальный возраст должен быть меньше максимального"
            )
        if attrs["min_age"] < 12:
            raise ValidationError("Минимальный возраст не может быть меньше 12")
        if attrs["max_age"] > 100:
            raise ValidationError("Максимальный возраст не может быть больше 100")
        return super().validate(attrs)

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
        return validated_data

    @staticmethod
    def validate_start_datetime(validated_data, hours):
        start_datetime = datetime.combine(
            validated_data["date"],
            validated_data["start_time"],
            tzinfo=localtime().tzinfo,
        )
        if start_datetime < localtime() + timedelta(hours=hours):
            raise ValidationError(
                f"Минимальное время до начала мероприятия - {hours} часов"
            )

    def create(self, validated_data):
        validated_data = self.prepare_location(validated_data)
        self.validate_start_datetime(validated_data, hours=6)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.prepare_location(validated_data)
        self.validate_start_datetime(validated_data, hours=5)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return {"id": instance.id}


class EventFastFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFastFilter
        fields = [
            "id",
            "name",
            "title",
        ]


class FilterQuerySerializer(Serializer):
    fast_filters = CharacterSeparatedField(
        child=serializers.IntegerField(), required=False
    )
    date = serializers.DateField(required=False)
    max_age = serializers.IntegerField(required=False)
    min_age = serializers.IntegerField(required=False)
    city = serializers.IntegerField(required=False, read_only=True)
    country = serializers.IntegerField(required=False, read_only=True)
    category = CharacterSeparatedField(child=serializers.IntegerField(), required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if categories := data.pop("category", None):
            filtered_themes = Theme.objects.filter(
                categories__id__in=categories
            ).distinct()
            data["themes"] = ThemeSerializer(
                filtered_themes, many=True, context={"categories": categories}
            ).data
        if fast_filters := data.get("fast_filters"):
            filters = EventFastFilter.objects.filter(id__in=fast_filters)
            data["fast_filters"] = EventFastFilterSerializer(filters, many=True).data
        return data
