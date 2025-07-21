from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.api.serializers import EventPriceDetailsSerializer


class EventPriceDetailsView(APIView):
    def post(self, request):
        serializer = EventPriceDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
