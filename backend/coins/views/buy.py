from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coins.serializers import BuyCoinsSerializer
from payment.payment_manager import PaymentManager


class BuyCoinsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BuyCoinsSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_type = serializer.validated_data["product_type"]
        product = serializer.validated_data["product"]
        payment_url, uuid = PaymentManager().buy(
            product_type=product_type,
            product_id=product.pk,
            product=product,
            user=request.user,
            base_url=request.build_absolute_uri("/")[:-1],
        )
        return Response({"url": payment_url, "uuid": uuid})
