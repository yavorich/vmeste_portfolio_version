from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.fields import (
    ObjectField,
    IntegerField,
    TextField,
    BooleanField,
)

from api.models import Event, Location, EventParticipant, User, Country, City, Category
from api.enums import Gender


@registry.register_document
class EventDocument(Document):
    id = IntegerField()
    uuid = TextField()
    is_close_event = BooleanField()
    is_draft = BooleanField()
    title = TextField()
    max_age = IntegerField()
    min_age = IntegerField()
    cover = TextField()
    short_description = TextField()
    location = ObjectField(
        properties={
            "name": TextField(),
            "address": TextField(),
        }
    )
    total_male = IntegerField()
    total_female = IntegerField()
    date_and_time = TextField()
    date_and_year = TextField()
    day_and_time = TextField()
    start_timestamp = IntegerField()
    end_timestamp = IntegerField()
    organizer = ObjectField(
        properties={
            "id": IntegerField(),
        }
    )
    country = ObjectField(
        properties={
            "id": IntegerField(),
        }
    )
    city = ObjectField(
        properties={
            "id": IntegerField(),
        }
    )
    categories = ObjectField(
        properties={
            "id": IntegerField(),
        }
    )
    participants = ObjectField(
        properties={
            "user": ObjectField(
                properties={
                    "id": IntegerField(),
                    "gender": TextField(),
                }
            ),
            "stats": ObjectField(
                properties={
                    "men": TextField(),
                    "women": TextField(),
                }
            ),
            "free_places": ObjectField(
                properties={
                    "male": IntegerField(),
                    "female": IntegerField(),
                    "total": IntegerField(),
                }
            ),
        }
    )

    class Index:
        name = "event"

    class Django:
        model = Event
        related_models = [EventParticipant, Country, City, Category, Location, User]

    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Event):
            return related_instance.objects.all()
        if isinstance(related_instance, EventParticipant):
            return related_instance.event
        if isinstance(related_instance, (Country, City, Category, Location)):
            return related_instance.events.all()
        if isinstance(related_instance, User):
            return Event.objects.filter_organizer_or_participant(related_instance)

    @staticmethod
    def prepare_participants(instance: Event):
        participants = instance.get_participants()
        male = participants.filter(user__gender=Gender.MALE).count()
        female = participants.filter(user__gender=Gender.FEMALE).count()
        total = male + female
        return {
            "user": [{"id": p.user.id, "gender": p.user.gender} for p in participants],
            "stats": {
                "men": f"{male}/{instance.total_male}",
                "women": f"{female}/{instance.total_female}",
            },
            "free_places": {
                "male": instance.total_male - male,
                "female": instance.total_female - female,
                "total": instance.total_male + instance.total_female - total,
            },
        }
