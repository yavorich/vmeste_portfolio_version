from django.db import models


class Occupation(models.Model):
    title = models.CharField("Название", max_length=255)

    class Meta:
        verbose_name = "Профессия"
        verbose_name_plural = "Профессии"

    def __str__(self) -> str:
        return self.title
