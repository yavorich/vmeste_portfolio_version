from rest_framework.permissions import BasePermission

from api.models import Event


class IsEventOrganizer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.organizer == user


class IsEventOrganizerOrParticipant(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.organizer == user or event.participants.filter(user=user).exists()


class IsMediaTimeValid(BasePermission):
    def has_permission(self, request, view):
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.is_valid_media_time()
