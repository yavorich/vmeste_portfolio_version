from rest_framework import serializers
from django.db.models import Q
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from api.models import User, Notification, EventParticipant
from api.serializers import CategoryTitleSerializer


class ProfilePartialUpdateSerializer(serializers.ModelSerializer):
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
            "interests",
            "about_me",
        ]

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.filter(~Q(pk=user.pk), email=value).exists():
            return serializers.ValidationError("Такой email уже существует.")
        if user.email != value:
            user.email_is_confirmed = False
            user.save()
        return value


class ProfileUpdateSerializer(ProfilePartialUpdateSerializer):
    class Meta(ProfilePartialUpdateSerializer.Meta):
        fields = ProfilePartialUpdateSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
        ]
        extra_kwargs = {
            "avatar": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {"required": True},
            "gender": {"required": True},
            "email": {"required": True},
        }


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    unread_notify = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    country = serializers.CharField(source="country.name", allow_null=True)
    city = serializers.CharField(source="city.name", allow_null=True)
    occupation = serializers.CharField(source="occupation.name", allow_null=True)
    interests = CategoryTitleSerializer(many=True)
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
            "interests",
            "about_me",
            "stats",
        ]

    def get_age(self, obj: User):
        return relativedelta(now().date(), obj.date_of_birth).years

    def get_unread_notify(self, obj: User):
        return Notification.objects.filter(user=obj, read=False).count()

    def get_stats(self, obj: User):
        participation = EventParticipant.objects.filter(user=obj)
        organized = participation.filter(is_organizer=True).count()
        signed = participation.filter(is_organizer=False).count()
        visited = participation.filter(has_confirmed=True).count()
        return {"organized": organized, "signed": signed, "visited": visited}


class SelfProfileRetrieveSerializer(ProfileRetrieveSerializer):
    subscription_days = serializers.SerializerMethodField()
    is_trial = serializers.BooleanField(source="subscription.is_trial", allow_null=True)

    class Meta(ProfileRetrieveSerializer.Meta):
        fields = ProfileRetrieveSerializer.Meta.fields + [
            "email",
            "phone_number",
            "telegram",
            "subscription_days",
            "is_trial",
        ]

    def get_subscription_days(self, obj: User):
        if not obj.subscription_expires:
            return 0
        return (obj.subscription_expires - now()).days


class SelfProfileDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]
