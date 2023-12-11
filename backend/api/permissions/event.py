from rest_framework.permissions import BasePermission

from api.models import Event


class IsEventOrganizer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            event = Event.objects.get(id=view.kwargs["event_id"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_id"])
        return event.organizer == user
