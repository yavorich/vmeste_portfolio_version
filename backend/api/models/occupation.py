from django.db import models


class Occupation(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"
