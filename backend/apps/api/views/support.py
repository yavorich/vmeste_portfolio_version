from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.admin_history.models import ActionFlag, HistoryLog
from apps.api.models import (
    SupportRequestTheme,
    SupportRequestMessage,
    SupportRequestType,
)
from apps.api.serializers import (
    SupportThemeListSerializer,
    SupportMessageCreateSerializer,
)


class SupportThemeListView(ListAPIView):
    queryset = SupportRequestTheme.objects.all()
    serializer_class = SupportThemeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        _type = self.request.query_params.get("type")
        if _type not in set(SupportRequestType):
            raise ValidationError(
                "Параметр 'type' не указан или имеет неверное значение. "
                + f"Ожидаемые значения: {[e.value for e in SupportRequestType]}"
            )
        return queryset.filter(type=_type)


class SupportMessageCreateView(CreateAPIView):
    queryset = SupportRequestMessage.objects.all()
    serializer_class = SupportMessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context
