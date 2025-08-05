from django.contrib import admin
from apps.payment.models import OrgPaymentProxy, PartPaymentProxy, TinkoffTransaction
from apps.admin_history.admin import site


@admin.register(OrgPaymentProxy, site=site)
class OrgPaymentProxyAdmin(admin.ModelAdmin):
    list_display = [
        "organizer_id",
        "event_title",
        "event_date",
        "event_place",
        "amount",
        "payment_date",
    ]

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

    @admin.display(description="Сумма оплаты (руб)")
    def amount(self, obj: PartPaymentProxy):
        return obj.price

    @admin.display(description="Дата оплаты")
    def payment_date(self, obj: PartPaymentProxy):
        return obj.updated_at


@admin.register(PartPaymentProxy, site=site)
class PartPaymentProxyAdmin(admin.ModelAdmin):
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
        return obj.updated_at

    @admin.display(description="Кол-во купленных билетов")
    def ticket_count(self, obj: PartPaymentProxy):
        return 1

    @admin.display(description="Номера билетов")
    def ticket_ids(self, obj: PartPaymentProxy):
        return obj.ticket_id

    @admin.display(description="Вознаграждение сервиса (%)")
    def service_reward(self, obj: PartPaymentProxy):
        return obj.service_reward


@admin.register(TinkoffTransaction, site=site)
class TinkoffTransactionAdmin(admin.ModelAdmin):
    pass
