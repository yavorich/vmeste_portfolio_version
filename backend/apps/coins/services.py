from apps.coins.models import CoinOffer, CoinSubscription
from apps.payment.models import ProductType


def buy_product(product_type, product_id, user):
    if product_type == ProductType.COINS:
        model = CoinOffer
    elif product_type == ProductType.SUBSCRIPTION:
        model = CoinSubscription
    else:
        raise NotImplementedError

    instance = model.objects.get(pk=product_id)
    instance.buy(user)
