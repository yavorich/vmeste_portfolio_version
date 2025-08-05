from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

from apps.api.models import User, Theme
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
    payment_type = CharField(source="get_payment_type_display")
    available_for_user = SerializerMethodField()

    class Meta:
        model = Theme
        fields = [
            "id",
            "title",
            "payment_type",
            "price",
            "commission_percent",
            "available_for_user",
            "sub",
        ]

    def get_available_for_user(self, obj: Theme):
        user_status = self.context.get("request").user.status
        if user_status == User.Status.FREE:
            return obj.payment_type == Theme.PaymentType.FREE
        if user_status == User.Status.MASTER:
            return obj.payment_type in [
                Theme.PaymentType.FREE,
                Theme.PaymentType.MASTER,
            ]
        return True
