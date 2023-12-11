from rest_framework_bulk import BulkUpdateModelMixin
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from api.models import Notification
from api.serializers import NotificationListSerializer, NotificationBulkUpdateSerializer


class NotificationListUpdateApiView(BulkUpdateModelMixin, ListAPIView):
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = {
        "GET": NotificationListSerializer,
        "PATCH": NotificationBulkUpdateSerializer,
    }

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def patch(self, request, *args, **kwargs):
        return self.partial_bulk_update(request, *args, **kwargs)
