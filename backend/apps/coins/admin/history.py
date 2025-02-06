from django.contrib import admin

from apps.admin_history.admin import site
from apps.coins.models import WalletHistory


@admin.register(WalletHistory, site=site)
class WalletHistoryAdmin(admin.ModelAdmin):
    fields = ("date", "operation_type", "_value", "_user")
    readonly_fields = fields
    list_display = ("id",) + fields
    list_display_links = list_display
    ordering = ("-date",)

    @admin.display(description="Количество")
    def _value(self, obj):
        match obj.operation_type:
            case WalletHistory.OperationType.SPEND:
                return f"-{obj.value}"

            case (
                WalletHistory.OperationType.REFUND
                | WalletHistory.OperationType.REPLENISHMENT
            ):
                return f"+{obj.value}"

        return obj.value

    @admin.display(description="Пользователь")
    def _user(self, obj):
        return obj.wallet.user

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
