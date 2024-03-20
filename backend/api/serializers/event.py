from rest_framework import serializers
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
)
from django.utils.timezone import localtime, datetime, timedelta
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from django.db.models import Q
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
    CategorySerializer,
    ThemeSerializer,
    ThemeCategoriesSerializer,
)
from api.documents import EventDocument
from api.models import EventFastFilter
from core.serializers import CustomFileField
from core.utils import validate_file_size
from .support import SupportMessageCreateSerializer


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
            "date": obj.date,
        }

    def get_am_i_organizer(self, obj: Event):
        user = self.context.get("user")
        if not user.is_authenticated:
            return False
        return user.id == obj.organizer.id

    def get_am_i_registered(self, obj: Event):
        user = self.context.get("user")
        if not user.is_authenticated:
            return False
        participant = obj.get_participant(user=user)
        return participant is not None

    def get_am_i_confirmed(self, obj: Event):
        user = self.context.get("user")
        if not user.is_authenticated:
            return False
        participant = obj.get_participant(user=user)
        return getattr(participant, "has_confirmed", False)

    def get_are_there_free_places(self, obj: Event):
        user = self.context.get("user")
        if not user.is_authenticated:
            return False
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

    def get_media(self, obj: Event):
        return obj.is_valid_media_time()

    def get_sign_and_edit(self, obj: Event):
        return obj.is_valid_sign_and_edit_time()

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
        fields = ["id", "first_name", "last_name", "avatar"]


class EventDetailSerializer(EventMixin, ModelSerializer):
    location = LocationSerializer()
    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()
    theme = ThemeSerializer(allow_null=True)
    categories = CategorySerializer(many=True)
    state = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()
    am_i_organizer = serializers.SerializerMethodField()
    am_i_registered = serializers.SerializerMethodField()
    are_there_free_places = serializers.SerializerMethodField()
    am_i_confirmed = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    sign_and_edit = serializers.SerializerMethodField()
    unread_messages = serializers.SerializerMethodField()

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
            "short_description",
            "location",
            "total_male",
            "total_female",
            "stats_men",
            "stats_women",
            "date_and_year",
            "day_and_time",
            "date",
            "start_datetime",
            "end_datetime",
            "theme",
            "categories",
            "state",
            "organizer",
            "am_i_organizer",
            "am_i_registered",
            "are_there_free_places",
            "did_organizer_marking",
            "am_i_confirmed",
            "media",
            "sign_and_edit",
            "is_draft",
            "unread_messages",
        ]

    def get_start_datetime(self, obj: Event):
        return obj.start_datetime.astimezone(localtime().tzinfo)

    def get_end_datetime(self, obj: Event):
        return obj.end_datetime.astimezone(localtime().tzinfo)

    def get_unread_messages(self, obj: Event):
        user = self.context["user"]
        if user.is_authenticated:
            return obj.chat.messages.filter(~Q(read__user=user)).count()
        return 0


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
    country_name = serializers.CharField(write_only=True)
    city_name = serializers.CharField(write_only=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all())
    categories = serializers.ListField(child=serializers.IntegerField())
    location_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    cover = CustomFileField(validators=[validate_file_size], read_only=False)

    class Meta:
        model = Event
        fields = [
            "id",
            "cover",
            "title",
            "country_name",
            "city_name",
            "location_name",
            "address",
            "latitude",
            "longitude",
            "date",
            "start_time",
            "end_time",
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
        extra_kwargs["cover"].update({"read_only": False})

    def prepare_location(self, validated_data: dict, instance: Event | None = None):
        validated_data["country"], _ = Country.objects.get_or_create(
            name=validated_data.pop("country_name")
        )
        validated_data["city"], _ = City.objects.get_or_create(
            name=validated_data.pop("city_name"), country=validated_data["country"]
        )
        cover = (
            validated_data["cover"]
            if isinstance(validated_data["cover"], InMemoryUploadedFile)
            else instance.location.cover
        )

        validated_data["location"], _ = Location.objects.get_or_create(
            country=validated_data["country"],
            city=validated_data["city"],
            address=validated_data.pop("address"),
            name=validated_data.pop("location_name"),
            defaults={
                "latitude": validated_data.pop("latitude"),
                "longitude": validated_data.pop("longitude"),
                "status": Location.Status.UNKNOWN,
                "cover": cover,
            },
        )

        return validated_data

    def validate_start_datetime(self, validated_data, hours):
        start_datetime = datetime.combine(
            validated_data["date"],
            validated_data["start_time"],
            tzinfo=localtime().tzinfo,
        )
        if start_datetime < localtime() + timedelta(hours=hours):
            raise ValidationError(
                {"error": f"Минимальное время до начала мероприятия - {hours} часов"}
            )

    def validate_age(self, validated_data):
        if validated_data["min_age"] >= validated_data["max_age"]:
            raise ValidationError(
                {"error": "Минимальный возраст должен быть меньше максимального"}
            )
        if validated_data["min_age"] < 13:
            raise ValidationError(
                {"error": "Минимальный возраст не может быть меньше 13"}
            )
        if validated_data["max_age"] > 100:
            raise ValidationError(
                {"error": "Максимальный возраст не может быть больше 100"}
            )

    def create(self, validated_data):
        validated_data = self.prepare_location(validated_data)
        self.validate_start_datetime(validated_data, hours=2)
        self.validate_age(validated_data)
        if not isinstance(validated_data.get("cover"), InMemoryUploadedFile):
            raise ValidationError(
                {"error": "Обложка события не является корректным файлом"}
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.prepare_location(validated_data, instance=instance)
        self.validate_start_datetime(validated_data, hours=2)
        self.validate_age(validated_data)
        if not isinstance(validated_data.get("cover"), InMemoryUploadedFile):
            validated_data.pop("cover", None)
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
            data["themes"] = ThemeCategoriesSerializer(
                filtered_themes, many=True, context={"categories": categories}
            ).data
        if fast_filters := data.get("fast_filters"):
            filters = EventFastFilter.objects.filter(id__in=fast_filters)
            data["fast_filters"] = EventFastFilterSerializer(filters, many=True).data
        return data


class EventSignSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = []

    def update(self, instance: Event, validated_data):
        user = self.context["user"]
        if instance.get_free_places(gender=user.gender) == 0:
            raise ValidationError(
                {"error": "На данное мероприятие не осталось свободных мест."}
            )

        if not instance.is_valid_age_to_sign(user=user):
            raise ValidationError(
                {"error": "Ваш возраст не подходит для записи на событие."}
            )

        EventParticipant.objects.get_or_create(
            event=instance, user=user
        )
        return instance


class EventCancelSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = []

    def update(self, instance: Event, validated_data):
        user = self.context["user"]
        participant = instance.get_participant(user=user)
        valid_time = instance.is_valid_sign_and_edit_time()

        if not participant:
            raise ValidationError(
                {"error": "Пользователь не является участником/организатором события"}
            )

        if participant.is_organizer:
            if not valid_time:
                raise ValidationError({"error": "Время отмены события истекло."})
            instance.is_draft = True
            instance.save()
        else:
            if not valid_time:
                raise ValidationError(
                    {"error": "Время отмены участия в событии истекло."}
                )
            participant.delete()

        return instance


class EventReportSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = []

    def update(self, instance: Event, validated_data):
        request = self.context["request"]
        user = self.context["user"]
        if instance.organizer == user:
            raise ValidationError(
                {"error": "Вы не можете пожаловаться на своё событие"}
            )
        serializer = SupportMessageCreateSerializer(
            data=request.data, context={"event": instance, "user": user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return instance


class EventConfirmSerializer(ModelSerializer):

    class Meta:
        model = Event
        fields = []

    def update(self, instance: Event, validated_data):
        participant = instance.get_participant(user=self.context["user"])
        if not participant:
            raise ValidationError(
                {"error": "Пользователь не является участником/организатором"}
            )
        participant.has_confirmed = True
        participant.save()
        return instance
