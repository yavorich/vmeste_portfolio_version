from django.db.models import TextChoices


class Gender(TextChoices):
    MALE = "M", "male"
    FEMALE = "F", "female"
