from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from api.serializers import (
    ProfileUpdateSerializer,
    ProfilePartialUpdateSerializer,
    ProfileRetrieveSerializer,
    SelfProfileRetrieveSerializer,
    SelfProfileDestroySerializer,
)
from api.models import User


class ProfileUpdateViewSet(UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = {
        "update": ProfileUpdateSerializer,
        "partial_update": ProfilePartialUpdateSerializer,
    }
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        result = serializer.save()
        result.profile_is_completed = True
        result.save()
        return result


class ProfileDetailViewSet(RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.is_mine():
            if self.action == 'retrieve':
                return SelfProfileRetrieveSerializer
            elif self.action == 'destroy':
                return SelfProfileDestroySerializer
        return super().get_serializer_class()

    def is_mine(self):
        return self.kwargs["pk"] == self.request.user.pk

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])
