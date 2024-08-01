from rest_framework.serializers import ModelSerializer

from coins.models import Wallet


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("balance", "unlimited", "unlimited_until")
