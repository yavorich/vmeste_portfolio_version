from rest_framework.serializers import ModelSerializer

from coins.models import CoinSubscription


class CoinSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = CoinSubscription
        fields = ("id", "price", "period_text")
