from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api.services import get_event_object
from api.models import Event, EventParticipant


class EventPublishedSignViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()

    def get_object(self):
        return get_event_object(self.kwargs["pk"])

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        user = request.user
        obj = self.get_object()
        participant = obj.get_participant(user)
        user_is_organizer = user == obj.organizer

        if obj.is_draft:
            raise ValidationError("Событие ещё не опубликовано")

        if not obj.is_active:
            raise ValidationError("Событие удалено или заблокировано")

        if participant is not None or user_is_organizer:
            raise ValidationError("Пользователь уже записан или является организатором")

        if obj.get_free_places(user.gender) == 0:
            raise ValidationError("На данное мероприятие не осталось свободных мест")

        if not obj.is_valid_sign_time():
            raise ValidationError("Время записи на мероприятие истекло")

        EventParticipant.objects.create(event=obj, user=self.request.user)
        return Response(
            {"message": "Запись на мероприятие прошла успешно"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        user = request.user
        obj = self.get_object()
        participant = obj.get_participant(user)
        user_is_organizer = user == obj.organizer

        if participant is None and not user_is_organizer:
            raise ValidationError("Пользователь не является участником/организатором")

        if user_is_organizer:
            if not obj.is_valid_sign_time():
                raise ValidationError("Нельзя отменить: до начала менее 3 часов")

            obj.is_draft = True
            obj.save()
            return Response(
                {"message": "Мероприятие отменено и добавлено в черновики"},
                status=status.HTTP_201_CREATED,
            )

        participant.delete()
        return Response(
            {"message": "Запись на мероприятие отменена"},
            status=status.HTTP_201_CREATED,
        )
