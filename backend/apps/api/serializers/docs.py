from rest_framework import serializers
from django.utils.timezone import localtime

from apps.admin_history.models import HistoryLog, ActionFlag
from apps.admin_history.utils import get_model_field_label
from apps.api.models import Docs


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = ["name", "text"]
        extra_kwargs = {f: {"required": False} for f in fields}

    def update(self, instance: Docs, validated_data):
        user = self.context["user"]
        name = instance.name
        field = None
        if name == Docs.Name.AGREEMENT and not user.agreement_applied_at:
            user.agreement_applied_at = localtime()
            field = "agreement_applied_at"
        if name == Docs.Name.RULES:
            user.event_rules_applied = True
            field = "event_rules_applied"
        if name == Docs.Name.OFFER:
            user.offer_applied = True
            field = "offer_applied"
        user.save()
        if field is not None:
            HistoryLog.objects.log_actions(
                user_id=user.pk,
                queryset=[user],
                action_flag=ActionFlag.CHANGE,
                change_message=[
                    {"changed": {"fields": [get_model_field_label(user, field)]}}
                ],
                is_admin=False,
            )
        return instance
