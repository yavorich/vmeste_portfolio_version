from django.db import models
from .event import Event
from .profile import Profile


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event, related_name="participants", on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        Profile, related_name="events", on_delete=models.CASCADE
    )
    is_organizer = models.BooleanField()
