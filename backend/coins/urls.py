from django.urls import path

from coins.views import (
    CoinOfferView,
    CoinSubscriptionView,
    ActivatePromoCodeView,
    BuyCoinsView,
)

urlpatterns = [
    path("offer/", CoinOfferView.as_view(), name="coin_offer"),
    path("subscription/", CoinSubscriptionView.as_view(), name="coin_subscription"),
    path(
        "promo_code/activate/",
        ActivatePromoCodeView.as_view(),
        name="activate_promo_code",
    ),
    path("buy/", BuyCoinsView.as_view(), name="buy_coins"),
]
