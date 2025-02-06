from django.contrib.admin.options import get_content_type_for_model
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CharField,
    EmailField,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.utils.timezone import localtime
from phonenumber_field.serializerfields import PhoneNumberField

from apps.admin_history.models import HistoryLog, ActionFlag
from apps.admin_history.utils import get_object_data_from_obj
from apps.api.models import User, Subscription, DeletedUser
from apps.api.services import generate_confirmation_code
from apps.api.tasks import send_mail_confirmation_code, send_phone_confirmation_code
from config.settings import DEBUG


class PhoneAuthSendCodeSerializer(Serializer):
    phone_number = PhoneNumberField(region="RU")
    confirmation_code = CharField(default=generate_confirmation_code())

    def create(self, validated_data):
        user = authenticate(
            self.context["request"], phone_number=validated_data["phone_number"]
        )
        if not user:
            user = DeletedUser.objects.filter(
                phone_number=validated_data["phone_number"]
            ).first()
            if user is not None:
                user.restore()
                HistoryLog.objects.log_action(
                    user_id=user.pk,
                    content_type_id=get_content_type_for_model(User).pk,
                    object_id=user.pk,
                    object_repr=str(user),
                    action_flag=ActionFlag.ADDITION,
                    change_message="Восстановил",
                    object_data=get_object_data_from_obj(user),
                )
            else:
                subscription, created = Subscription.objects.get_or_create(
                    is_trial=True
                )
                user = User.objects.create_user(
                    phone_number=validated_data["phone_number"],
                    subscription=subscription,
                    subscription_expires=localtime() + subscription.duration,
                )
                HistoryLog.objects.log_actions(
                    user_id=user.pk,
                    queryset=[user],
                    action_flag=ActionFlag.ADDITION,
                    change_message=[{"added": {}}],
                    is_admin=False,
                )

        user.confirmation_code = validated_data["confirmation_code"]
        user.save()
        if not DEBUG:
            send_phone_confirmation_code.delay(
                user.phone_number, user.confirmation_code
            )
        return user

    def to_representation(self, instance):
        return {}


class EmailAuthSendCodeSerializer(ModelSerializer):
    confirmation_code = CharField(default=generate_confirmation_code())

    class Meta:
        model = User
        fields = ["email", "confirmation_code"]

    def validate_email(self, value):
        if self.context["user"].email != value:
            raise ValidationError({"error": "Неправильная почта"})
        return value

    def create(self, validated_data):
        user = self.context["user"]
        user.confirmation_code = validated_data["confirmation_code"]
        user.save()
        if not DEBUG:
            send_mail_confirmation_code.delay(user.email, user.confirmation_code)
        return user

    def to_representation(self, instance):
        return {}


class PhoneAuthSerializer(Serializer):
    phone_number = CharField(max_length=20)
    confirmation_code = CharField(max_length=5)

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise ValidationError({"error": "Неверный номер телефона"})
        return value

    def create(self, validated_data):
        request = self.context["request"]
        user: User = authenticate(request, phone_number=validated_data["phone_number"])
        code = validated_data["confirmation_code"]
        if code != ("11111" if DEBUG else user.confirmation_code):
            raise ValidationError({"error": "Неверный код подтверждения"})
        user.is_registered = True
        user.save()
        login(
            request,
            user,
            backend="api.backends.auth.PhoneAuthBackend",
        )
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            "id": instance.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "profile_is_completed": instance.profile_is_completed,
        }


class EmailAuthSerializer(Serializer):
    email = EmailField()
    confirmation_code = CharField(max_length=5)

    def validate_email(self, value):
        if self.context["user"].email != value:
            raise ValidationError({"error": "Неправильная почта"})
        return value

    def validate_confirmation_code(self, value):
        user = self.context["user"]
        if value != ("11111" if DEBUG else user.confirmation_code):
            raise ValidationError({"error": "Неверный код подтверждения"})
        return value

    def create(self, validated_data):
        user = self.context["user"]
        user.email_is_confirmed = True
        user.is_registered = True
        user.save()
        return user

    def to_representation(self, instance):
        return {}
