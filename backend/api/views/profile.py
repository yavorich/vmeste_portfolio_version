from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from api.serializers import (
    SelfProfileUpdateSerializer,
    SelfProfilePartialUpdateSerializer,
    ProfileRetrieveSerializer,
    SelfProfileRetrieveSerializer,
    SelfProfileDestroySerializer,
    SupportMessageCreateSerializer,
)
from api.models import User


class SelfProfileViewSet(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = {
        "retrieve": SelfProfileRetrieveSerializer,
        "update": SelfProfileUpdateSerializer,
        "partial_update": SelfProfilePartialUpdateSerializer,
        "destroy": SelfProfileDestroySerializer,
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


class AlienProfileViewSet(RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileRetrieveSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def get_serializer_class(self):
        serializer_classes = {
            "retrieve": ProfileRetrieveSerializer,
            "report": SupportMessageCreateSerializer,
        }
        return serializer_classes[self.action]

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        if not user.is_active:
            raise ValidationError({"error": "Пользователь заблокирован"})
        return user

    @action(detail=True, methods=["post"])
    def report(self, request, pk=None):
        user = request.user
        profile = self.get_object()
        if user == profile:
            raise ValidationError("Вы не можете пожаловаться на свой профиль")

        serializer = SupportMessageCreateSerializer(
            data=request.data, context={"profile": profile, "user": user}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Вы успешно пожаловались на профиль"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
