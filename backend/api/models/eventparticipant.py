from django.db import models
from .event import Event
from .user import User


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event, related_name="participants", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="events", on_delete=models.CASCADE
    )
    is_organizer = models.BooleanField()
