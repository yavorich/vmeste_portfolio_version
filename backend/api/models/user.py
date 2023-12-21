import os

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from api.enums import Gender
from .country import Country
from .city import City
from .category import Category
from .occupation import Occupation
from .subscription import Subscription


def get_upload_path(instance, filename):
    return os.path.join("users", str(instance.pk), "avatar", filename)


class UserManager(BaseUserManager):
    use_in_migrations = True

    @staticmethod
    def normalize_phone_number(phone_number):
        return "".join([ch for ch in phone_number if ch.isdigit() or ch == "+"])

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, password=password, **extra_fields)
        if password is None:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(phone_number, password, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    phone_number_regex = RegexValidator(regex=r"^\+7\d{10}$")
    phone_number = models.CharField(
        validators=[phone_number_regex], max_length=20, unique=True
    )
    confirmation_code = models.CharField(max_length=5, null=True)
    profile_is_completed = models.BooleanField(default=False)
    first_name = models.CharField(_("Имя"), null=True)
    last_name = models.CharField(_("Фамилия"), null=True)
    date_of_birth = models.DateField(_("Дата рождения"), null=True)
    gender = models.CharField(_("Пол"), choices=Gender.choices, max_length=6, null=True)
    avatar = models.ImageField(_("Аватар"), upload_to=get_upload_path, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(null=True)
    email_is_confirmed = models.BooleanField(default=False)
    country = models.ForeignKey(
        Country, related_name="users", on_delete=models.SET_NULL, null=True, blank=True
    )
    city = models.ForeignKey(
        City, related_name="users", on_delete=models.SET_NULL, null=True, blank=True
    )
    telegram = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.ForeignKey(
        Occupation,
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    interests = models.ManyToManyField(Category, related_name="users", blank=True)
    about_me = models.TextField(max_length=2000, null=True, blank=True)
    subscription = models.ForeignKey(
        Subscription, related_name="users", on_delete=models.SET_NULL, null=True
    )
    subscription_expires = models.DateTimeField(null=True)
    agreement_applied_at = models.DateTimeField(null=True)

    USERNAME_FIELD = "phone_number"

    objects = UserManager()

    def __str__(self) -> str:
        return self.phone_number

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_interests(self) -> list[str]:
        return "\n".join([str(i) for i in self.interests.all()])

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
