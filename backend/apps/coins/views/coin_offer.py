from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.coins.models import CoinOffer
from apps.coins.serializers import CoinOfferSerializer


class CoinOfferView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoinOfferSerializer
    queryset = CoinOffer.objects.order_by("coins")
