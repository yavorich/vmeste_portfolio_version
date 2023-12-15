from django.db import models
from django.utils.timezone import timedelta


class Subscription(models.Model):
    price = models.FloatField(default=0.0)
    duration = models.DurationField(default=timedelta(days=7))
    worth = models.TextField(default="")
    is_trial = models.BooleanField()
