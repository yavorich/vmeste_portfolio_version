from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from api.serializers import CategorySerializer, OccupationSerializer
from api.models import Category, Occupation


class InterestListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    queryset = Category.objects.all()


class OccupationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OccupationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    queryset = Occupation.objects.all()
