from rest_framework import serializers
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time

from api.models import Event
from api.serializers import LocationSerializer


class EventMarkingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(remove_fields=["city", "country"])
    date_and_year = serializers.SerializerMethodField()
    day_and_time = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "date_and_year",
            "day_and_time",
            "location",
        ]

    def get_date_and_year(self, obj: Event):
        return _date(obj.date, "j E, Y")

    def get_day_and_time(self, obj: Event):
        return (
            _date(obj.date, "l")
            + _time(obj.start_time, ", H:i")
            + _time(obj.end_time, "-H:i")
        )
