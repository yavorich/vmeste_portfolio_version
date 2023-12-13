from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

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
            return Response(
                {"message": "Событие ещё не опубликовано"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if participant is not None or user_is_organizer:
            return Response(
                {"message": "Пользователь уже записан или является организатором"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if obj.get_free_places(user.gender) == 0:
            return Response(
                {"message": "На данное мероприятие не осталось свободных мест"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not obj.is_valid_sign_time():
            return Response(
                {"message": "Время записи на мероприятие истекло"},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
            return Response(
                {"message": "Пользователь не является участником/организатором"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_is_organizer:
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
