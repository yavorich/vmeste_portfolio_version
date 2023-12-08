from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login

from api.serializers import (
    PhoneAuthSerializer,
    EmailAuthSerializer,
    PhoneAuthSendCodeSerializer,
    EmailAuthSendCodeSerializer,
)
from api.services import send_confirmation_code
from api.models import User


class AuthSendCodeView(APIView):
    permission_classes = {
        "phone": [AllowAny],
        "mail": [IsAuthenticated],  # AllowAny for test
    }
    serializer_class = {
        "phone": PhoneAuthSendCodeSerializer,
        "mail": EmailAuthSendCodeSerializer,
    }

    def get_permissions(self):
        _type = self.request.query_params.get("type")
        self.permission_classes = self.permission_classes[_type]
        return super(AuthSendCodeView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        serializer = self.serializer_class[_type](
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if _type == "phone":
            try:
                user = User.objects.get(phone_number=data["phone_number"])
            except User.DoesNotExist:
                user = User.objects.create_user(phone_number=data["phone_number"])
        elif _type == "mail":
            user = request.user
        user.confirmation_code = data["confirmation_code"]
        user.save()
        send_confirmation_code(user, _type)
        return Response(status=status.HTTP_201_CREATED)


class AuthView(APIView):
    permission_classes = {
        "phone": [AllowAny],
        "mail": [IsAuthenticated],  # AllowAny for test
    }
    serializer_class = {"phone": PhoneAuthSerializer, "mail": EmailAuthSerializer}

    def get_permissions(self):
        _type = self.request.query_params.get("type")
        self.permission_classes = self.permission_classes[_type]
        return super(AuthView, self).get_permissions()

    def post(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        serializer = self.serializer_class[_type](
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if _type == "phone":
            user = authenticate(request, phone_number=data["phone_number"])
            if user.confirmation_code == data["confirmation_code"]:
                login(
                    request,
                    user,
                    backend="api.backends.auth.PhoneAuthBackend",
                )
            else:
                return Response(
                    {"error": "Confirmation code is not valid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif _type == "mail":
            user = User.objects.get(email=data["email"])
            if user.confirmation_code == data["confirmation_code"]:
                user.email_is_confirmed = True
                user.save()

        refresh = RefreshToken.for_user(user)
        data = {
            "id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "profile_is_completed": user.profile_is_completed,
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
