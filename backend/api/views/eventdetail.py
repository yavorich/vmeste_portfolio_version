from rest_framework import generics, permissions
from rest_framework.response import Response
from ..models import Event, Notification
from ..serializers import EventDetailSerializer


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EventDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["user"] = self.request.user
        return context

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        if self.request.user.is_authenticated:
            unread_notify = Notification.objects.filter(
                user=self.request.user, read=False
            ).count()
            data["unread_notify"] = unread_notify
        return Response(data)
