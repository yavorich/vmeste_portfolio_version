from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from api.models import SupportRequestTheme, SupportRequestMessage
from api.serializers import SupportThemeListSerializer, SupportMessageCreateSerializer


class SupportThemeListView(ListAPIView):
    queryset = SupportRequestTheme.objects.all()
    serializer_class = SupportThemeListSerializer
    permission_classes = [IsAuthenticated]


class SupportMessageCreateView(CreateAPIView):
    queryset = SupportRequestMessage.objects.all()
    serializer_class = SupportMessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context
