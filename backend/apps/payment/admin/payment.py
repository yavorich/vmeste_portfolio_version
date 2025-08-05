from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources, fields

from apps.payment.models import OrgPaymentProxy, PartPaymentProxy, TinkoffTransaction
from apps.admin_history.admin import site


class PaymentResourceMixin:
    def dehydrate_organizer_id(self, obj):
        return obj.event.organizer.pk if obj.event else None

    def dehydrate_event_title(self, obj: PartPaymentProxy):
        return obj.event.title if obj.event else None

    def dehydrate_event_date(self, obj: PartPaymentProxy):
        return obj.event.date if obj.event else None

    def dehydrate_event_place(self, obj: PartPaymentProxy):
        if not obj.event:
            return None
        location = obj.event.location
        return f"{location.city}, {location.name}" if location else None

    def dehydrate_payer_id(self, obj: PartPaymentProxy):
        return obj.user.pk

    def dehydrate_payer_full_name(self, obj: PartPaymentProxy):
        return obj.user.get_full_name()

    def dehydrate_payment_amount(self, obj: PartPaymentProxy):
        return obj.price

    def dehydrate_payment_date(self, obj: PartPaymentProxy):
        return obj.updated_at.replace(tzinfo=None)

    def dehydrate_ticket_count(self, obj: PartPaymentProxy):
        return 1

    def dehydrate_ticket_ids(self, obj: PartPaymentProxy):
        return obj.ticket_id

    def dehydrate_service_reward(self, obj: PartPaymentProxy):
        return obj.service_reward


class OrgPaymentResource(PaymentResourceMixin, resources.ModelResource):
    organizer_id = fields.Field(column_name="ID организатора")
    event_title = fields.Field(column_name="Название встречи")
    event_date = fields.Field(column_name="Дата встречи")
    event_place = fields.Field(column_name="Город и место встречи")
    payment_amount = fields.Field(column_name="Сумма оплаты")
    payment_date = fields.Field(column_name="Дата оплаты")

    class Meta:
        model = OrgPaymentProxy
        fields = (
            "organizer_id",
            "event_title",
            "event_date",
            "event_place",
            "payment_amount",
            "payment_date",
        )


class PartPaymentResource(PaymentResourceMixin, resources.ModelResource):
    organizer_id = fields.Field(column_name="ID организатора")
    event_title = fields.Field(column_name="Название встречи")
    event_date = fields.Field(column_name="Дата встречи")
    event_place = fields.Field(column_name="Город и место встречи")
    payer_id = fields.Field(column_name="ID плательщика")
    payer_full_name = fields.Field(column_name="ФИО плательщика")
    payment_amount = fields.Field(column_name="Сумма оплаты")
    payment_date = fields.Field(column_name="Дата оплаты")
    ticket_count = fields.Field(column_name="Кол-во купленных билетов")
    ticket_ids = fields.Field(column_name="Номера билетов")
    service_reward = fields.Field(column_name="Вознаграждение сервиса")

    class Meta:
        model = PartPaymentProxy
        fields = (
            "organizer_id",
            "event_title",
            "event_date",
            "event_place",
            "payer_id",
            "payer_full_name",
            "payment_amount",
            "payment_date",
            "ticket_count",
            "ticket_ids",
            "service_reward",
        )


class PaymentAdminMixin:
    @admin.display(description="ID организатора")
    def organizer_id(self, obj: PartPaymentProxy):
        return obj.event.organizer.pk if obj.event else None

    @admin.display(description="Название встречи")
    def event_title(self, obj: PartPaymentProxy):
        return obj.event.title if obj.event else None

    @admin.display(description="Дата встречи")
    def event_date(self, obj: PartPaymentProxy):
        return obj.event.date if obj.event else None

    @admin.display(description="Город и место встречи")
    def event_place(self, obj: PartPaymentProxy):
        if not obj.event:
            return None
        location = obj.event.location
        return f"{location.city}, {location.name}" if location else None

    @admin.display(description="ID плательщика")
    def payer_id(self, obj: PartPaymentProxy):
        return obj.user.pk

    @admin.display(description="ФИО плательщика")
    def payer_full_name(self, obj: PartPaymentProxy):
        return obj.user.get_full_name()

    @admin.display(description="Сумма оплаты (руб)")
    def amount(self, obj: PartPaymentProxy):
        return obj.price

    @admin.display(description="Дата оплаты")
    def payment_date(self, obj: PartPaymentProxy):
        return obj.updated_at.date()

    @admin.display(description="Кол-во купленных билетов")
    def ticket_count(self, obj: PartPaymentProxy):
        return 1

    @admin.display(description="Номера билетов")
    def ticket_ids(self, obj: PartPaymentProxy):
        return obj.ticket_id

    @admin.display(description="Вознаграждение сервиса (%)")
    def service_reward(self, obj: PartPaymentProxy):
        return obj.service_reward
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = ...):
        return False


@admin.register(OrgPaymentProxy, site=site)
class OrgPaymentProxyAdmin(PaymentAdminMixin, ExportMixin, admin.ModelAdmin):
    resource_class = OrgPaymentResource
    list_display = [
        "organizer_id",
        "event_title",
        "event_date",
        "event_place",
        "amount",
        "payment_date",
    ]


@admin.register(PartPaymentProxy, site=site)
class PartPaymentProxyAdmin(PaymentAdminMixin, ExportMixin, admin.ModelAdmin):
    resource_class = PartPaymentResource
    list_display = [
        "organizer_id",
        "event_title",
        "event_date",
        "event_place",
        "payer_id",
        "payer_full_name",
        "amount",
        "payment_date",
        "ticket_count",
        "ticket_ids",
        "service_reward",
    ]


@admin.register(TinkoffTransaction, site=site)
class TinkoffTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "created_at",
        "updated_at",
        "status",
        "transaction_type",
        "product_type",
        "user",
        "event",
        "price",
    ]
