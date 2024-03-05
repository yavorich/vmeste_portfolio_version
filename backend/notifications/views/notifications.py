from rest_framework_bulk import BulkUpdateModelMixin
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from notifications.models import UserNotification
from notifications.serializers import (
    UserNotificationListSerializer,
    UserNotificationBulkUpdateSerializer,
)


class NotificationListUpdateApiView(BulkUpdateModelMixin, ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = {
        "GET": UserNotificationListSerializer,
        "PATCH": UserNotificationBulkUpdateSerializer,
    }

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def patch(self, request, *args, **kwargs):
        return self.partial_bulk_update(request, *args, **kwargs)
