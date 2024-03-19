from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from notifications.serializers import PushTokenSerializer


class PushTokenView(  # REVIEW: тут можно оставить только create и destroy
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = PushTokenSerializer

    def get_object(self):
        # REVIEW: query_params вместо data. Тут косяк моего кода)
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

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.push_tokens.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
