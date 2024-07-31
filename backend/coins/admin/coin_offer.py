from django.contrib import admin

from coins.models import CoinOffer


@admin.register(CoinOffer)
class CoinOfferAdmin(admin.ModelAdmin):
    fields = ("coins", "discount")
    ordering = ("coins",)
    list_display = ("coins", "discount", "price_with_discount")
    list_display_links = list_display

    @admin.display(description="Стоимость со скидкой, Р")
    def price_with_discount(self, obj):
        return obj.price_with_discount
