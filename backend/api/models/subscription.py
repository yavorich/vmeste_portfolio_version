from django.db import models


class Subscription(models.Model):
    price = models.FloatField()
    validity = models.IntegerField()
    worth = models.TextField()
    is_trial = models.BooleanField()
