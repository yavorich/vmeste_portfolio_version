from django.contrib import admin
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from dal.autocomplete import Select2, Select2Multiple

from apps.admin_history.admin import site
from apps.admin_history.models import HistoryLog, ActionFlag
from apps.admin_history.utils import get_object_data_from_obj

# from apps.coins.models import Wallet
from core.admin import ManyToManyMixin
from apps.api.models import (
    User,
    DeletedUser,
    Verification,
    LegalEntity,
    ConfirmationStatus,
)
from core.utils.short_text import short_text


class LegalEntityInline(admin.StackedInline):
    model = LegalEntity
    fields = (
        "image",
        "company_name",
        "legal_address",
        "resp_full_name",
        "resp_phone_number",
        "director_full_name",
        "inn",
        "bic",
        "bank_name",
        "current_account",
        "sites",
        "confirmed",
    )
    extra = 0


class VerificationInline(admin.StackedInline):
    model = Verification
    fields = ("document_file", "confirmed")
    extra = 0


# class WalletInline(admin.StackedInline):
#     model = Wallet
#     fields = ("balance", "unlimited_until")
#     min_num = 1
#     max_num = 1
#     can_delete = False


class InterestInline(admin.TabularInline):
    model = User.categories.through
    verbose_name = "Интерес"
    verbose_name_plural = "Интересы"


class UserForm(ModelForm):
    class Meta:
        widgets = {"categories": Select2Multiple()}


@admin.register(User, site=site)
class UserAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [VerificationInline, LegalEntityInline]
    form = UserForm
    list_display = [
        "is_active",
        "status",
        "id",
        "phone_number",
        "email",
        "_avatar",
        "first_name",
        "last_name",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        # "balance",
        "get_interests",
        "occupation",
        "agreement_applied_at",
    ]
    list_display_links = [
        "id",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "status",
                    "phone_number",
                    "email",
                    "avatar",
                    "first_name",
                    "last_name",
                    "gender",
                    "country",
                    "city",
                    "date_of_birth",
                    "telegram",
                    "occupation",
                    # "theme",
                    "categories",
                    "profile_is_completed",
                    "email_is_confirmed",
                    "subscription",
                    "subscription_expires",
                    "agreement_applied_at",
                    "last_login",
                    "is_added_bank_card",
                ]
            },
        )
    ]
    readonly_fields = ["is_added_bank_card", "status"]
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["block_users", "unblock_users"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_registered=True)

    # @admin.display(description="Баланс")
    # def balance(self, obj):
    #     return obj.wallet.balance

    @admin.display(description="Аватар")
    def _avatar(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<a href="{obj.avatar.url}">{short_text(obj.avatar.name, 20)}</a>'
            )
        return ""

    @admin.display(description="Интересы")
    def get_interests(self, obj):
        return self.links_to_objects(obj.categories.all())

    @admin.action(description="Заблокировать")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.display(description="Привязана банковская карта", boolean=True)
    def is_added_bank_card(self, obj):
        return obj.is_added_bank_card

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        user = form.instance

        if user.verification_status == ConfirmationStatus.CONFIRMED:
            if (
                user.legal_entity_status == ConfirmationStatus.CONFIRMED
                or user.is_added_bank_card
            ):
                user.status = User.Status.PROFI
            else:
                user.status = User.Status.MASTER

        else:
            user.status = User.Status.FREE

        user.save()


@admin.register(DeletedUser, site=site)
class DeletedUserAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [InterestInline]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "phone_number",
                    "email",
                    "avatar",
                    "first_name",
                    "last_name",
                    "gender",
                    "country",
                    "city",
                    "date_of_birth",
                    "telegram",
                    "occupation",
                    "profile_is_completed",
                    "email_is_confirmed",
                    "subscription",
                    "subscription_expires",
                    "agreement_applied_at",
                    "last_login",
                ]
            },
        )
    ]
    list_display = [
        "id",
        "phone_number",
        "email",
        "avatar",
        "first_name",
        "last_name",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        "get_interests",
        "occupation",
        "agreement_applied_at",
    ]
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["restore_users"]

    @admin.display(description="Интересы")
    def get_interests(self, obj):
        return self.links_to_objects(obj.categories.all())

    @admin.action(description="Восстановить")
    def restore_users(self, request, queryset):
        for user in queryset:
            user.restore()
            HistoryLog.objects.log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(User).pk,
                object_id=user.pk,
                object_repr=str(user),
                action_flag=ActionFlag.ADDITION,
                change_message="Восстановил",
                object_data=get_object_data_from_obj(user),
            )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
