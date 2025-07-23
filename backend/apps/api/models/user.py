import os
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime
from dateutil.relativedelta import relativedelta
from phonenumber_field.modelfields import PhoneNumberField

from apps.api.enums import Gender
from core.model_fields import CompressedImageField


def get_upload_path(instance, filename):
    return os.path.join("users", str(instance.pk), "avatar", filename)


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True), {}


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db, hints=self._hints).filter(
            is_deleted=False
        )

    @staticmethod
    def normalize_phone_number(phone_number):
        return "".join([ch for ch in phone_number if ch.isdigit() or ch == "+"])

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")
        phone_number = self.normalize_phone_number(str(phone_number))
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


class AllUserManager(UserManager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset()


class User(AbstractBaseUser, PermissionsMixin):
    class Status(models.TextChoices):
        FREE = "FREE", "Free"
        MASTER = "MASTER", "Master"
        PRO = "PRO", "Profi"

    status = models.CharField(
        "Статус", max_length=8, choices=Status.choices, default=Status.FREE
    )

    username = None
    phone_number = PhoneNumberField(_("Телефон"), unique=True, region="RU")
    confirmation_code = models.CharField(
        _("Код подтверждения"), max_length=5, blank=True, null=True
    )
    profile_is_completed = models.BooleanField(_("Профиль заполнен"), default=False)
    first_name = models.CharField(_("Имя"), blank=True, null=True)
    last_name = models.CharField(_("Фамилия"), blank=True, null=True)
    date_of_birth = models.DateField(_("Дата рождения"), blank=True, null=True)
    gender = models.CharField(
        _("Пол"), choices=Gender.choices, max_length=6, blank=True, null=True
    )
    avatar = CompressedImageField(
        _("Аватар"),
        max_width=360,
        max_height=360,
        upload_to=get_upload_path,
        default="defaults/avatar.png",
    )
    is_active = models.BooleanField(_("Активен"), default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(_("Почта"), blank=True, null=True)
    email_is_confirmed = models.BooleanField(_("Почта подтверждена"), default=False)
    country = models.ForeignKey(
        "api.Country",
        verbose_name=_("Страна"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        "api.City",
        verbose_name=_("Город"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    telegram = models.CharField(_("Телеграм"), max_length=255, null=True, blank=True)
    occupation = models.ForeignKey(
        "api.Occupation",
        verbose_name=_("Профессия"),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        "api.Category",
        verbose_name=_("Категории"),
        related_name="users",
        blank=True,
    )
    about_me = models.TextField(_("Обо мне"), max_length=2000, null=True, blank=True)
    subscription = models.ForeignKey(
        "api.Subscription",
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
    event_rules_applied = models.BooleanField(_("Правила сервиса"), default=False)
    offer_applied = models.BooleanField(_("Оферта"), default=False)
    sending_push = models.BooleanField(_("Отправка уведомлений"), default=True)
    receive_recs = models.BooleanField(_("Рекомендовать события"), default=True)

    uuid = models.UUIDField(default=uuid4)
    is_registered = models.BooleanField(_("Зарегистрирован"), default=False)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"

    objects = UserManager()
    all_objects = AllUserManager()

    def __str__(self) -> str:
        return f"{self.get_full_name()} {self.phone_number}".lstrip()

    def get_full_name(self) -> str:
        first_name = self.first_name if self.first_name is not None else ""
        last_name = self.last_name if self.last_name is not None else ""
        return f"{first_name} {last_name}".strip()

    def clean(self):
        if self.age is None:
            return

        if self.age < 18:
            raise ValidationError(
                {"date_of_birth": "Возраст должен быть не менее 18 лет"}
            )
        elif self.age > 100:
            raise ValidationError(
                {"date_of_birth": "Возраст должен быть не более 100 лет"}
            )

    @property
    def age(self) -> int:
        if self.date_of_birth is None:
            return

        return relativedelta(localtime().date(), self.date_of_birth).years

    @property
    def categories_ordering(self):
        return self.categories.order_by("title")

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(using=using)
        return 1, {}

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def bank_card(self):
        try:
            return self.payment_info
        except ObjectDoesNotExist:
            from apps.payment.models import PaymentInfo

            return PaymentInfo.objects.create(user=self)

    @property
    def is_added_bank_card(self):
        from apps.payment.payment_manager import PaymentManager

        return PaymentManager().is_added_card(self)


class DeletedUserManager(UserManager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset().filter(is_deleted=True)


class DeletedUser(User):
    objects = DeletedUserManager()

    class Meta:
        proxy = True
        verbose_name = "Пользователь"
        verbose_name_plural = "Удалённые пользователи"

    def restore(self):
        self.is_deleted = False
        self.save()
