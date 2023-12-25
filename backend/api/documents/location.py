from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.fields import (
    TextField,
    IntegerField,
    GeoPointField,
    ObjectField,
    KeywordField,
)
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.analysis import token_filter

from api.models import Location, City
from core.utils import convert_file_to_base64

edge_ngram_completion_filter = token_filter(
    "edge_ngram_completion_filter", type="edge_ngram", min_gram=3, max_gram=128
)

edge_ngram_completion = analyzer(
    "edge_ngram_completion",
    tokenizer="standard",
    filter=["lowercase", edge_ngram_completion_filter],
)


@registry.register_document
class LocationDocument(Document):
    id = IntegerField()
    cover = TextField()
    name = TextField(fields={"raw": KeywordField()}, analyzer=edge_ngram_completion)
    coords = GeoPointField(attr="coords_field_indexing")
    address = TextField(fields={"raw": KeywordField()}, analyzer=edge_ngram_completion)
    discount = IntegerField()
    city = ObjectField(
        properties={
            "id": IntegerField(),
        }
    )
    status = TextField()

    class Index:
        name = "location"

    class Django:
        model = Location
        related_models = [
            City,
        ]

    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    }

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Location):
            return related_instance.objects.all()
        if isinstance(related_instance, City):
            return related_instance.locations.all()

    def prepare_cover(instance: Location):
        return convert_file_to_base64(instance.cover.file)
