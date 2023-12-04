from rest_framework.serializers import ModelSerializer
from api.models import Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]
