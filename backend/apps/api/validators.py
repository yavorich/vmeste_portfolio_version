from string import digits

from django.core.exceptions import ValidationError


def validate_only_digits(value):
    if set(value) > set(digits):
        raise ValidationError("Должен состоять из цифр")
