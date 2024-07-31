from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from coins.models import CoinSubscription
from coins.serializers import CoinSubscriptionSerializer


class CoinSubscriptionView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoinSubscriptionSerializer
    queryset = CoinSubscription.objects.all()
