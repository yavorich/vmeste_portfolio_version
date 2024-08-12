from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter

from apps.api.serializers import (
    CategorySerializer,
    OccupationSerializer,
    ThemeSerializer,
)
from apps.api.models import Category, Occupation, Theme


class CategoryListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        queryset = Category.objects.filter(theme=self.kwargs["pk"])
        return queryset


class InterestListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class OccupationListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = OccupationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    queryset = Occupation.objects.all()


class ThemeListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ThemeSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    queryset = Theme.objects.all()
