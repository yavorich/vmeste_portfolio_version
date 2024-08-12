import django_eventstream
from django.urls import path, include

from payment.views import (
    PaymentNotificationHookView,
    SuccessPaymentView,
    FailPaymentView,
)


urlpatterns = [
    path("webhook/", PaymentNotificationHookView.as_view(), name="payment_webhook"),
    path("success/", SuccessPaymentView.as_view(), name="payment_success"),
    path("fail/", FailPaymentView.as_view(), name="payment_fail"),
    path(
        "events/<uuid>/",
        include(django_eventstream.urls),
        {"format-channels": ["payment_{uuid}"]},
    ),
]
