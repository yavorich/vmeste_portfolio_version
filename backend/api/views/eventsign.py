from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from api.models import Event, EventParticipant
from django.shortcuts import get_object_or_404


class EventSignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, action):
        event = get_object_or_404(Event, id=id)
        if action == "sign":
            if not event.published:
                return Response(
                    {"message": "Событие ещё не опубликовано"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if event.get_participant(self.request.user) is not None:
                return Response(
                    {"message": "Пользователь уже записан или является организатором"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not event.has_free_places():
                return Response(
                    {"message": "На данное мероприятие не осталось свободных мест"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not event.is_valid_sign_time():
                return Response(
                    {"message": "Время записи на мероприятие истекло"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            EventParticipant.objects.create(event=event, user=self.request.user)
            return Response(
                {"message": "Запись на мероприятие выполнена"},
                status=status.HTTP_201_CREATED,
            )
        elif action == "cancel":
            participant = event.get_participant(self.request.user)
            if participant is None:
                return Response(
                    {"message": "Пользователь не является участником/организатором"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if participant.is_organizer:
                event.published = False
                event.save()
                return Response(
                    {"message": "Мероприятие отменено и добавлено в черновики"},
                    status=status.HTTP_201_CREATED,
                )
            participant.delete()
            return Response(
                {"message": "Запись на мероприятие отменена"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": f"Неверное действие: {action}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
