from rest_framework.serializers import Serializer, SerializerMethodField
from django.template.defaultfilters import date as _date
from ..models import Event


class DateTimeSerializer(Serializer):
    date_and_year = SerializerMethodField()
    day_and_time = SerializerMethodField()

    def get_date_and_year(self, obj: Event):
        return _date(obj.start_datetime, "j E, Y")

    def get_day_and_time(self, obj: Event):
        return _date(obj.start_datetime, "l, H:i") + _date(obj.end_datetime, "-H:i")
