from django.db import models

from .user import User


class EventParticipant(models.Model):
    # event = models.ForeignKey(
    #     "Event", related_name="participants", on_delete=models.CASCADE
    # )
    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)
    has_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Участник события"
        verbose_name_plural = "Участники события"
