from django.urls import path

from coins.views import CoinOfferView, CoinSubscriptionView


urlpatterns = [
    path("offer/", CoinOfferView.as_view(), name="coin_offer"),
    path("subscription/", CoinSubscriptionView.as_view(), name="coin_subscription"),
]
