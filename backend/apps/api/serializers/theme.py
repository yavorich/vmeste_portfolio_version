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
    sub = CategorySerializer(source="categories_ordering", many=True)

    class Meta:
        model = Theme
        fields = ["id", "title", "organizer_price", "participant_price", "sub"]
