from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.fields import (
    ObjectField,
    IntegerField,
    TextField,
    BooleanField,
    KeywordField,
    DateField,
    FileField,
)
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.analysis import token_filter

from apps.api.models import (
    Event,
    Location,
    EventParticipant,
    User,
    Country,
    City,
    Category,
    Theme,
)
from apps.api.enums import Gender

edge_ngram_completion_filter = token_filter(
    "edge_ngram_completion_filter", type="edge_ngram", min_gram=1, max_gram=128
)

edge_ngram_completion = analyzer(
    "edge_ngram_completion",
    tokenizer="standard",
    filter=["lowercase", edge_ngram_completion_filter],
)


@registry.register_document
class EventDocument(Document):
    id = IntegerField()
    uuid = TextField()
    is_close_event = BooleanField()
    is_draft = BooleanField()
    is_active = BooleanField()
    title = TextField(fields={"raw": KeywordField()}, analyzer=edge_ngram_completion)
    max_age = IntegerField()
    min_age = IntegerField()
    cover = FileField()
    short_description = TextField(
        fields={"raw": KeywordField()}, analyzer=edge_ngram_completion
    )
    location = ObjectField(
        properties={
            "name": TextField(
                fields={"raw": KeywordField()}, analyzer=edge_ngram_completion
            ),
            "address": TextField(
                fields={"raw": KeywordField()}, analyzer=edge_ngram_completion
            ),
        }
    )
    total_male = IntegerField()
    total_female = IntegerField()
    date_and_time = TextField()
    date_and_year = TextField()
    day_and_time = TextField()
    date = DateField()
    start_datetime = DateField()
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
    sign_price = IntegerField()

    class Index:
        name = "event"

    class Django:
        model = Event
        related_models = [
            EventParticipant,
            Country,
            City,
            Theme,
            Category,
            Location,
            User,
        ]

    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Event):
            return related_instance.objects.all()
        if isinstance(related_instance, EventParticipant):
            return related_instance.event
        if isinstance(related_instance, (Country, City, Theme, Category, Location)):
            return related_instance.events.all()
        if isinstance(related_instance, User):
            return Event.objects.filter_participant(related_instance)

    @staticmethod
    def prepare_participants(instance: Event):
        participants = instance.participants.all()
        male = participants.filter(user__gender=Gender.MALE).count()
        female = participants.filter(user__gender=Gender.FEMALE).count()
        total = male + female
        return {
            "user": [{"id": p.user.id, "gender": p.user.gender} for p in participants],
            "stats": {
                "men": f"{male}/{instance.total_male}"
                if instance.total_male is not None
                else str(male),
                "women": f"{female}/{instance.total_female}"
                if instance.total_female is not None
                else str(female),
            },
            "free_places": {
                "male": instance.total_male - male
                if instance.total_male is not None
                else None,
                "female": instance.total_female - female
                if instance.total_female is not None
                else None,
                "total": instance.total_male + instance.total_female - total
                if instance.total_male is not None and instance.total_female is not None
                else None,
            },
        }

    @staticmethod
    def prepare_organizer(instance: Event):
        organizer = instance.organizer
        return {"id": getattr(organizer, "id", None)}

    @staticmethod
    def prepare_location(instance: Event):
        location = instance.location
        return {
            "name": location.name,
            "address": f"{location.city.name}, {location.address}",
        }
