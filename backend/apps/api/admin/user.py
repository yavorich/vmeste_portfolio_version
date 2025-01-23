from django.contrib import admin
from django.contrib.admin.options import get_content_type_for_model

from apps.admin_history.admin import site
from apps.admin_history.models import HistoryLog, ActionFlag
from apps.coins.models import Wallet
from core.admin import ManyToManyMixin
from apps.api.models import User, DeletedUser


class WalletInline(admin.StackedInline):
    model = Wallet
    fields = ("balance", "unlimited_until")
    min_num = 1
    max_num = 1
    can_delete = False


class InterestInline(admin.TabularInline):
    model = User.categories.through
    verbose_name = "Интерес"
    verbose_name_plural = "Интересы"


@admin.register(User, site=site)
class UserAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [WalletInline, InterestInline]
    list_display = [
        "is_active",
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
    list_display_links = [
        "id",
    ]
    list_editable = [
        "is_active",
        "phone_number",
        "email",
        "avatar",
        "first_name",
        "last_name",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        "occupation",
        "agreement_applied_at",
    ]
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
    readonly_fields = []
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["block_users", "unblock_users"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_registered=True)

    @admin.display(description="Интересы")
    def get_interests(self, obj):
        return self.links_to_objects(obj.categories.all())

    @admin.action(description="Заблокировать")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(DeletedUser, site=site)
class DeletedUserAdmin(ManyToManyMixin, admin.ModelAdmin):
    inlines = [WalletInline, InterestInline]
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
            )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
