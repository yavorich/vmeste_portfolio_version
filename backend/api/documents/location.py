from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.fields import TextField, IntegerField, FloatField
from django_elasticsearch_dsl.registries import registry

from api.models import Location


@registry.register_document
class LocationDocument(Document):
    id = IntegerField()
    cover = TextField()
    name = TextField()
    latitude = FloatField()
    longitude = FloatField()
    address = TextField()
    discount = IntegerField()

    class Index:
        name = "location"

    class Django:
        model = Location
        related_models = []

    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Location):
            return related_instance.objects.all()
