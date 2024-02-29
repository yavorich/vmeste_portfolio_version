import os

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from api.enums import Gender
from .country import Country
from .city import City
from .category import Category
from .theme import Theme
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
    phone_number = PhoneNumberField(_("Телефон"), unique=True, region="RU")
    confirmation_code = models.CharField(max_length=5, blank=True, null=True)
    profile_is_completed = models.BooleanField(_("Профиль заполнен"), default=False)
    first_name = models.CharField(_("Имя"), blank=True, null=True)
    last_name = models.CharField(_("Фамилия"), blank=True, null=True)
    date_of_birth = models.DateField(_("Дата рождения"), blank=True, null=True)
    gender = models.CharField(
        _("Пол"), choices=Gender.choices, max_length=6, blank=True, null=True
    )
    avatar = models.ImageField(
        _("Аватар"), upload_to=get_upload_path, default="defaults/avatar.png"
    )
    is_active = models.BooleanField(_("Активен"), default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(_("Почта"), blank=True, null=True)
    email_is_confirmed = models.BooleanField(_("Почта подтверждена"), default=False)
    country = models.ForeignKey(
        Country,
        verbose_name=_("Страна"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        verbose_name=_("Город"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    telegram = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.ForeignKey(
        Occupation,
        verbose_name=_("Профессия"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    theme = models.ForeignKey(
        Theme,
        verbose_name=_("Тема"),
        related_name="users",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("Категории"),
        related_name="users",
        blank=True,
    )
    about_me = models.TextField(_("Обо мне"), max_length=2000, null=True, blank=True)
    subscription = models.ForeignKey(
        Subscription,
        verbose_name=_("Подписка"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
    )
    subscription_expires = models.DateTimeField(
        _("Дата окончания подписки"), blank=True, null=True
    )
    agreement_applied_at = models.DateTimeField(
        _("Дата принятия соглашения"), null=True
    )
    event_rules_applied = models.BooleanField(default=False)
    offer_applied = models.BooleanField(default=False)
    sending_push = models.BooleanField(default=True)
    receive_recs = models.BooleanField(default=True)

    USERNAME_FIELD = "phone_number"

    objects = UserManager()

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
