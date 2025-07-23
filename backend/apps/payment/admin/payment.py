from django.contrib import admin
from apps.payment.models.payment_proxy import OrgPaymentProxy, PartPaymentProxy


@admin.register(OrgPaymentProxy)
class OrgPaymentProxyAdmin(admin.ModelAdmin):
    pass


@admin.register(PartPaymentProxy)
class PartPaymentProxyAdmin(admin.ModelAdmin):
    pass
