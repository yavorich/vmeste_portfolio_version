from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, ChoiceField, IntegerField

from coins.models import CoinOffer, CoinSubscription


class BuyCoinsSerializer(Serializer):
    product_type = ChoiceField(choices=("coins", "subscription"))
    product_id = IntegerField()

    def validate(self, attrs):
        product_type = attrs["product_type"]
        match product_type:
            case "coins":
                model = CoinOffer
            case "subscription":
                model = CoinSubscription
            case _:
                raise NotImplementedError

        try:
            attrs["product"] = model.objects.get(pk=attrs["product_id"])
        except ObjectDoesNotExist:
            raise ValidationError({"product_id": "Продукт не найден"})

        return attrs
