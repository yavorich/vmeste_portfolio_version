from rest_framework.serializers import ModelSerializer, SerializerMethodField
from ..models import Event, EventParticipant
from ..enums import Gender
from .location import LocationSerializer


class EventSerializer(ModelSerializer):
    location = LocationSerializer()
    stats_men = SerializerMethodField()
    stats_women = SerializerMethodField()
    am_i_organizer = SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "title", "max_age", "min_age",
                  "cover", "short_description", "location",
                  "stats_men", "stats_women", "day_and_time",
                  "am_i_organizer"]

    def get_am_i_organizer(self, obj: Event):
        profile = self.context.get("profile")
        if profile:
            participant = EventParticipant.objects.filter(
                event=obj, profile=profile)[0]
            return participant.is_organizer
        return None

    def get_stats(self, obj: Event, gender: Gender):
        total_participants = obj.participants.count()
        count = obj.participants.filter(
            profile__gender=gender).count()
        if total_participants > 0:
            return f"{count}/{total_participants}"
        return "0/0"

    def get_stats_men(self, obj: Event):
        return self.get_stats(obj, Gender.MALE)

    def get_stats_women(self, obj: Event):
        return self.get_stats(obj, Gender.FEMALE)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get("profile"):
            data.pop("am_i_organizer")
        return data
