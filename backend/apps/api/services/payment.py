"""
Deprecated
"""


def do_payment_on_create(event):
    # если не черновик и организатор должен оплатить
    if not event.is_draft and event.organizer_will_pay:
        _organizer_spend(event)


def do_payment_on_update(old_event, event):
    if not event.is_draft and old_event.is_draft:  # публикация
        if event.organizer_will_pay:
            _organizer_spend(event)

            # возврат, если кто-то уже оплатил участие
            for participant in (
                event.participants.filter(is_organizer=False, payed__gt=0)
                .select_related("user")
                .iterator()
            ):
                participant.user.wallet.refund(participant.payed)

    elif event.is_draft and not old_event.is_draft:  # возвращение в черновик
        do_payment_refund(event)


def do_payment_refund(event):
    # возврат для всех
    for participant in (
        event.participants.filter(payed__gt=0).select_related("user").iterator()
    ):
        participant.user.wallet.refund(participant.payed)


def _organizer_spend(event):
    # оплата организатором
    organizer_price = event.theme.organizer_price
    organizer_participant = event.participants.get(is_organizer=True)
    organizer_participant.user.wallet.spend(organizer_price)
    organizer_participant.payed = organizer_price
    organizer_participant.save()
