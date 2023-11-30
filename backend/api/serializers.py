from rest_framework import serializers
from . import models
from .enums import Gender


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "title"]


class ThemeSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Theme
        fields = ["id", "title", "categories"]

    def get_categories(self, obj):
        categories = [c for c in obj.categories.all()
                      if c.id in self.context["categories"]]
        if categories:
            return CategorySerializer(categories, many=True).data
        return None


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ["name", "address"]


class EventSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    stats_men = serializers.SerializerMethodField()
    stats_women = serializers.SerializerMethodField()

    def get_stats(self, obj: models.Event, gender: Gender):
        total_participants = obj.participants.count()
        count = obj.participants.filter(
            profile__gender=gender).count()
        if total_participants > 0:
            return f"{count}/{total_participants}"
        return "0/0"

    def get_stats_men(self, obj: models.Event):
        return self.get_stats(obj, Gender.MALE)

    def get_stats_women(self, obj: models.Event):
        return self.get_stats(obj, Gender.FEMALE)

    class Meta:
        model = models.Event
        fields = ["id", "title", "max_age", "min_age",
                  "cover", "short_description", "location",
                  "stats_men", "stats_women", "day_and_time"]
