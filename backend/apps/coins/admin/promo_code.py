from django.contrib import admin

from apps.admin_history.admin import site
from apps.coins.models import PromoCode


@admin.register(PromoCode, site=site)
class PromoCodeAdmin(admin.ModelAdmin):
    fields = ("code", "coins", "quantity")
    list_display = ("code", "coins", "quantity", "user_activated_quantity")
    list_display_links = list_display

    @admin.display(description="Использовано активаций")
    def user_activated_quantity(self, obj):
        return obj.user_activated_quantity
