from rest_framework.serializers import ModelSerializer, IntegerField

from coins.models import CoinOffer


class CoinOfferSerializer(ModelSerializer):
    price_with_discount = IntegerField()

    class Meta:
        model = CoinOffer
        fields = ("id", "coins", "discount", "price_with_discount")
