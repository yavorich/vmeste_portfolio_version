from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from coins.models import CoinSubscription


@admin.register(CoinSubscription)
class CoinSubscriptionAdmin(SortableAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("price",)}),
        ("Период", {"fields": ("period_type", "quantity")}),
    )
    list_display = ("sort_value", "price", "quantity", "period_type")
    list_display_links = list_display
    ordering = ("sort_value",)
