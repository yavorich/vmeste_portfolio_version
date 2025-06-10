from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.utils.timezone import localtime
from dateutil.relativedelta import relativedelta
from rest_framework.exceptions import ValidationError

from apps.api.models import EventParticipant, User
from apps.api.serializers import CategorySerializer, CitySerializer, CountrySerializer
from apps.coins.serializers import WalletSerializer
from core.utils import validate_file_size


class SelfProfilePartialUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(validators=[validate_file_size], required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "country",
            "city",
            "email",
            "telegram",
            "occupation",
            "theme",
            "categories",
            "about_me",
        ]
        extra_kwargs = {f: {"required": False} for f in fields}

    def update(self, instance, validated_data):
        avatar = validated_data.get("avatar", None)
        if not isinstance(avatar, (InMemoryUploadedFile)):
            validated_data.pop("avatar", None)
        return super().update(instance, validated_data)

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.filter(~Q(pk=user.pk), email=value).exists():
            raise serializers.ValidationError({"error": "Такой email уже существует."})
        if user.email != value:
            user.email_is_confirmed = False
            user.save()
        return value


class SelfProfileUpdateSerializer(SelfProfilePartialUpdateSerializer):
    class Meta(SelfProfilePartialUpdateSerializer.Meta):
        fields = SelfProfilePartialUpdateSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {"required": True},
            "gender": {"required": True},
            "email": {"required": True},
        }

    def validate_date_of_birth(self, value):
        age = relativedelta(localtime().date(), value).years
        if age < 18:
            raise ValidationError({"error": "Возраст не может быть меньше 18"})
        elif age > 90:
            raise ValidationError({"error": "Возраст не может быть больше 90"})
        return value


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    unread_notify = serializers.SerializerMethodField()
    country = CountrySerializer(allow_null=True)
    city = CitySerializer(allow_null=True)
    occupation = serializers.CharField(source="occupation.title", allow_null=True)
    categories = CategorySerializer(many=True, source="categories_ordering")
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "unread_notify",
            "id",
            "avatar",
            "age",
            "gender",
            "country",
            "city",
            "occupation",
            "first_name",
            "last_name",
            "categories",
            "about_me",
            "stats",
            "email_is_confirmed",
        ]

    def get_unread_notify(self, obj: User):
        return obj.notifications.filter(read=False).count()

    def get_stats(self, obj: User):
        participation = EventParticipant.objects.filter(
            user=obj, event__is_active=True, event__is_draft=False
        )
        past_participation = participation.filter(
            event__end_datetime__lte=localtime(),
        )
        organized = participation.filter(is_organizer=True).count()
        signed = participation.count() - organized
        visited = past_participation.filter(has_confirmed=True).count()
        skipped = past_participation.count() - visited
        return {
            "organized": organized,
            "signed": signed,
            "visited": visited,
            "skipped": skipped,
        }


class SelfProfileRetrieveSerializer(ProfileRetrieveSerializer):
    subscription_days = serializers.SerializerMethodField()
    is_trial = serializers.BooleanField(source="subscription.is_trial", allow_null=True)
    wallet = WalletSerializer()

    class Meta(ProfileRetrieveSerializer.Meta):
        fields = ProfileRetrieveSerializer.Meta.fields + [
            "date_of_birth",
            "email",
            "phone_number",
            "telegram",
            "subscription_days",
            "is_trial",
            "wallet",
        ]

    def get_subscription_days(self, obj: User):
        if not obj.subscription_expires:
            return 0
        return (obj.subscription_expires - localtime()).days


class SelfProfileDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]
