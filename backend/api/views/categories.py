from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from api.serializers import (
    CategorySerializer,
    OccupationSerializer,
    ThemeSerializer,
)
from api.models import Category, Occupation, Theme


class CategoryListView(ListAPIView):
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


class ThemeListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThemeSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    queryset = Theme.objects.all()
