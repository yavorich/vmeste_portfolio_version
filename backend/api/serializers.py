from rest_framework import serializers
from . import models
from .enums import Gender


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ["name", "address"]


class EventSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    stats_men = serializers.SerializerMethodField()
    stats_women = serializers.SerializerMethodField()

    def get_stats_men(self, obj: models.Event):
        total_participants = obj.participants.count()
        men_count = obj.participants.filter(
            profile__gender=Gender.MALE).count()
        if total_participants > 0:
            return f"{men_count}/{total_participants}"
        return "0/0"

    def get_stats_women(self, obj: models.Event):
        total_participants = obj.participants.count()
        women_count = obj.participants.filter(
            profile__gender=Gender.FEMALE).count()
        if total_participants > 0:
            return f"{women_count}/{total_participants}"
        return "0/0"

    class Meta:
        model = models.Event
        fields = ["id", "title", "max_age", "min_age",
                  "cover", "short_description", "location",
                  "stats_men", "stats_women", "day_and_time"]
