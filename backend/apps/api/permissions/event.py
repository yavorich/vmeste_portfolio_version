from rest_framework.permissions import BasePermission

from apps.api.models import Event


class IsEventOrganizer(BasePermission):
    message = "Пользователь не является организатором мероприятия."

    def has_permission(self, request, view):
        user = request.user
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.participants.get(is_organizer=True).user == user


class IsEventParticipant(BasePermission):
    message = "Пользователь не является участником мероприятия"

    def has_permission(self, request, view):
        user = request.user
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.participants.filter(user=user).exists()


class IsMediaTimeValid(BasePermission):
    message = "Срок актуальности медиафайлов события истёк."

    def has_permission(self, request, view):
        try:
            event = Event.objects.get(id=view.kwargs["event_pk"])
        except Event.DoesNotExist:
            event = Event.objects.get(uuid=view.kwargs["event_pk"])
        return event.is_valid_media_time()


class IsTicketScanner(BasePermission):
    message = "Пользователь не является проверяющим"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                event = Event.objects.get(id=view.kwargs["event_pk"])
            except Event.DoesNotExist:
                event = Event.objects.get(uuid=view.kwargs["event_pk"])
            return event.scanner_account == request.user
        return False
