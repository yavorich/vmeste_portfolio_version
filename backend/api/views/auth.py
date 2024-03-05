from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.utils.timezone import localtime

from api.serializers import (
    PhoneAuthSerializer,
    EmailAuthSerializer,
    PhoneAuthSendCodeSerializer,
    EmailAuthSendCodeSerializer,
)
from api.services import send_confirmation_code
from api.models import User, Subscription
from config.settings import DEBUG


class AuthSendCodeView(APIView):
    serializer_class = {
        "phone": PhoneAuthSendCodeSerializer,
        "mail": EmailAuthSendCodeSerializer,
    }

    def get_permissions(self):
        permission_classes = {
            "phone": [AllowAny],
            "mail": [IsAuthenticated],
        }
        _type = self.request.query_params.get("type")
        self.permission_classes = permission_classes[_type]
        return super(AuthSendCodeView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        serializer = self.serializer_class[_type](
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if _type == "phone":
            user = authenticate(request, phone_number=data["phone_number"])
            if not user:
                subscription, created = Subscription.objects.get_or_create(
                    is_trial=True
                )
                user = User.objects.create_user(
                    phone_number=data["phone_number"],
                    subscription=subscription,
                    subscription_expires=localtime() + subscription.duration,
                )
        elif _type == "mail":
            user = request.user
        user.confirmation_code = data["confirmation_code"]
        user.save()
        send_confirmation_code(user, _type)
        return Response(status=status.HTTP_201_CREATED)


class AuthView(APIView):
    serializer_class = {"phone": PhoneAuthSerializer, "mail": EmailAuthSerializer}

    def get_permissions(self):
        permission_classes = {
            "phone": [AllowAny],
            "mail": [IsAuthenticated],
        }
        _type = self.request.query_params.get("type")
        self.permission_classes = permission_classes[_type]
        return super(AuthView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        serializer = self.serializer_class[_type](
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        return getattr(self, f"_{_type}")(request, data)

    @staticmethod
    def validate_code(user, data):
        if data["confirmation_code"] == ("11111" if DEBUG else user.confirmation_code):
            return
        raise ValidationError({"error": "Неверный код подтверждения"})

    def _mail(self, request, data):
        user = User.objects.get(email=data["email"])
        self.validate_code(user, data)
        user.email_is_confirmed = True
        user.save()
        return Response({"success": "Почта подтверждена"})

    def _phone(self, request, data):
        user = authenticate(request, phone_number=data["phone_number"])
        self.validate_code(user, data)
        login(
            request,
            user,
            backend="api.backends.auth.PhoneAuthBackend",
        )
        refresh = RefreshToken.for_user(user)
        data = {
            "id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "profile_is_completed": user.profile_is_completed,
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
