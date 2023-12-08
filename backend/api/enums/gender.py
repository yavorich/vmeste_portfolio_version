from django.db.models import TextChoices


class Gender(TextChoices):
    MALE = "male", "Мужской"
    FEMALE = "female", "Женский"
