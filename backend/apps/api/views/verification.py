from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

from apps.api.models import User
from apps.api.serializers import VerificationSerializer


class VerificationView(
    CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericAPIView
):
    permission_classes = (IsAuthenticated,)
    serializer_class = VerificationSerializer

    def get_object(self):
        try:
            return self.request.user.verification
        except ObjectDoesNotExist:
            raise NotFound
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(confirmed=False)
        user = self.request.user
        user.status = User.Status.FREE
        user.save()
