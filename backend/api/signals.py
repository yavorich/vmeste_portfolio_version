from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from api.models import EventParticipant


@receiver(post_delete, sender=EventParticipant)
def update_event_document(sender, instance: EventParticipant, **kwargs):
    registry.update(instance.event)
