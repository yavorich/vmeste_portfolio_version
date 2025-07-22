from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.api.models import Theme
from .category import CategorySerializer


class ThemeCategoriesSerializer(ModelSerializer):
    categories = SerializerMethodField()

    class Meta:
        model = Theme
        fields = ["id", "title", "categories"]

    def get_categories(self, obj):
        categories = obj.categories.filter(pk__in=self.context["categories"]).order_by(
            "title"
        )
        if categories:
            return CategorySerializer(categories, many=True).data
        return None


class ThemeSerializer(ModelSerializer):

    class Meta:
        model = Theme
        fields = ["id", "title", "payment_type", "price", "commission_percent"]
