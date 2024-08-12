from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.api.serializers import (
    PhoneAuthSerializer,
    EmailAuthSerializer,
    PhoneAuthSendCodeSerializer,
    EmailAuthSendCodeSerializer,
)


class AuthMixin:
    def get_serializer_class(self):
        _type = self.request.query_params.get("type")
        return self.serializer_class[_type]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


class AuthSendCodeView(AuthMixin, CreateAPIView):
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


class AuthView(AuthMixin, CreateAPIView):
    serializer_class = {
        "phone": PhoneAuthSerializer,
        "mail": EmailAuthSerializer,
    }

    def get_permissions(self):
        permission_classes = {
            "phone": [AllowAny],
            "mail": [IsAuthenticated],
        }
        _type = self.request.query_params.get("type")
        self.permission_classes = permission_classes[_type]
        return super(AuthView, self).get_permissions()
