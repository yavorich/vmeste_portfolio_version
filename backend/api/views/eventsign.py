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

        if obj.is_draft:
            raise ValidationError({"error": "Событие ещё не опубликовано"})

        if not obj.is_active:
            raise ValidationError({"error": "Событие удалено или заблокировано"})

        if participant is not None:
            raise ValidationError(
                {"error": "Пользователь уже записан или является организатором"}
            )

        if obj.get_free_places(user.gender) == 0:
            raise ValidationError(
                {"error": "На данное мероприятие не осталось свободных мест"}
            )

        if not obj.is_valid_sign_time():
            raise ValidationError({"error": "Время записи на мероприятие истекло"})

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

        if obj.is_draft or not obj.is_active:
            raise ValidationError(
                {"error": "Мероприятие уже отменено или заблокировано"}
            )

        if participant is None:
            raise ValidationError(
                {"error": "Пользователь не является участником/организатором"}
            )

        if participant.is_organizer:
            if not obj.is_valid_sign_time():
                raise ValidationError(
                    {
                        "error": "Нельзя отменить: до начала события осталось"
                        + " менее 1 часа"
                    }
                )

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
