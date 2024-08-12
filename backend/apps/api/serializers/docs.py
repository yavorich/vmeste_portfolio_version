from rest_framework import serializers
from django.utils.timezone import localtime

from apps.api.models import Docs


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = ["name", "text"]
        extra_kwargs = {f: {"required": False} for f in fields}

    def update(self, instance: Docs, validated_data):
        user = self.context["user"]
        name = instance.name
        if name == Docs.Name.AGREEMENT and not user.agreement_applied_at:
            user.agreement_applied_at = localtime()
        if name == Docs.Name.RULES:
            user.event_rules_applied = True
        if name == Docs.Name.OFFER:
            user.offer_applied = True
        user.save()
        return instance
