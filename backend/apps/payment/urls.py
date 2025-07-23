import django_eventstream
from django.urls import path, include

from apps.payment.views import (
    PaymentNotificationHookView,
    SuccessPaymentView,
    FailPaymentView,
    BankCardView,
    BankCardAddView,
)


urlpatterns = [
    path("webhook/", PaymentNotificationHookView.as_view(), name="payment_webhook"),
    path("success/", SuccessPaymentView.as_view(), name="payment_success"),
    path("fail/", FailPaymentView.as_view(), name="payment_fail"),
    path("bank_card/add/", BankCardAddView.as_view(), name="bank_card_add"),
    path("bank_card/", BankCardView.as_view(), name="bank_card"),
    path(
        "events/<uuid>/",
        include(django_eventstream.urls),
        {"format-channels": ["payment_{uuid}"]},
    ),
]
