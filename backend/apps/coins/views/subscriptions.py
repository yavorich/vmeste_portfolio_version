from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.coins.models import CoinSubscription
from apps.coins.serializers import CoinSubscriptionSerializer


class CoinSubscriptionView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoinSubscriptionSerializer
    queryset = CoinSubscription.objects.all()
