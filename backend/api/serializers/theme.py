from rest_framework.serializers import ModelSerializer, SerializerMethodField
from ..models import Theme
from .category import CategorySerializer


class ThemeSerializer(ModelSerializer):
    categories = SerializerMethodField()

    class Meta:
        model = Theme
        fields = ["id", "title", "categories"]

    def get_categories(self, obj):
        categories = [
            c for c in obj.categories.all() if c.id in self.context["categories"]
        ]
        if categories:
            return CategorySerializer(categories, many=True).data
        return None
