from apps.api.models import Event, Theme
from apps.payment.models import ProductType
from apps.payment.payment_manager import PaymentManager


def do_payment_on_create(event: Event, request):
    # если не черновик и организатор должен оплатить
    if not event.is_draft and event.theme.payment_type == Theme.PaymentType.MASTER:
        return _init_organizer_payment(event, request)
    return {}


def do_payment_on_sign(event: Event, request):
    if not event.is_draft and event.theme.payment_type == Theme.PaymentType.PROF:
        return _init_participant_payment(event, request)
    return {}


def do_payment_on_update(old_event: Event, event: Event, request):
    if not event.is_draft and old_event.is_draft:  # публикация
        if event.theme.payment_type == Theme.PaymentType.MASTER:
            _init_organizer_payment(event, request)
            do_payment_refund(event, participants_only=True)  # возврат участникам

    elif event.is_draft and not old_event.is_draft:  # возвращение в черновик
        do_payment_refund(event)  # возврат всем


def do_payment_refund(event, participants_only: bool = False):
    filter_kwargs = dict(payed__gt=0)
    if participants_only:
        filter_kwargs.update(dict(is_organizer=False))

    for participant in (
        event.participants.filter(**filter_kwargs).select_related("user").iterator()
    ):
        pass  # TODO: сделать возврат Тинькофф


def _init_organizer_payment(event: Event, request):
    # оплата организатором
    organizer_price = event.theme.price

    return PaymentManager().init_event_payment(
        event=event,
        user=event.participants.get(is_organizer=True).user,
        product_type=ProductType.ORGANIZATION,
        amount=organizer_price,
        base_url=request.build_absolute_uri("/")[:-1],
    )


def _init_participant_payment(event: Event, request):
    # оплата участником
    participant_price = event.sign_price

    return PaymentManager().init_event_payment(
        event=event,
        user=request.user,
        product_type=ProductType.PARTICIPANCE,
        amount=participant_price,
        base_url=request.build_absolute_uri("/")[:-1],
    )
