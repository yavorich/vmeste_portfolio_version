from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema

from account.permissions import AcceptAgreement, WithUserData
from notification.serializers import PushTokenSerializer


class PushTokenView(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericAPIView
):
    permission_classes = (IsAuthenticated, AcceptAgreement, WithUserData)
    serializer_class = PushTokenSerializer

    def get_object(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.request.user.push_tokens.filter(
            **serializer.validated_data
        ).first()
        if instance is None:
            raise NotFound
        return instance

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PushTokenSerializer,
        operation_description="device_os: 'android' or 'ios'",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.push_tokens.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
