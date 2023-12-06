from django.db import models

from .user import User


class Notification(models.Model):
    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )
    read = models.BooleanField(default=False)
