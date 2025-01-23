import json

from django.conf import settings
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Model,
    DateTimeField,
    ForeignKey,
    CASCADE,
    SET_NULL,
    TextField,
    CharField,
    BooleanField,
    PositiveSmallIntegerField,
    IntegerChoices,
    ManyToManyField,
    Manager,
)
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.text import get_text_list
from django.utils.translation import gettext_lazy as _, gettext


class ActionFlag(IntegerChoices):
    ADDITION = 1, _("Addition")
    CHANGE = 2, _("Change")
    DELETION = 3, _("Deletion")
    OTHER = 4, "Другое"


class HistoryLogManager(Manager):
    use_in_migrations = True

    def log_action(
        self,
        user_id,
        content_type_id,
        object_id,
        object_repr,
        action_flag,
        change_message="",
        *,
        is_admin=True
    ):
        if isinstance(change_message, list):
            change_message = json.dumps(change_message)
        return self.model.objects.create(
            user_id=user_id,
            content_type_id=content_type_id,
            object_id=str(object_id),
            object_repr=object_repr[:200],
            action_flag=action_flag,
            change_message=change_message,
            is_admin=is_admin,
        )

    def log_actions(
        self, user_id, queryset, action_flag, change_message="", *, is_admin=True
    ):
        if isinstance(change_message, list):
            change_message = json.dumps(change_message)

        log_entry_list = [
            self.model(
                user_id=user_id,
                content_type_id=ContentType.objects.get_for_model(
                    obj, for_concrete_model=False
                ).id,
                object_id=obj.pk,
                object_repr=str(obj)[:200],
                action_flag=action_flag,
                change_message=change_message,
                is_admin=is_admin,
            )
            for obj in queryset
        ]

        if log_entry_list and len(log_entry_list) == 1:
            instance = log_entry_list[0]
            instance.save()
            return instance

        return self.model.objects.bulk_create(log_entry_list)


class HistoryLog(Model):
    action_time = DateTimeField(
        _("action time"),
        default=timezone.now,
        editable=False,
    )
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        SET_NULL,
        verbose_name=_("user"),
        null=True,
    )
    content_type = ForeignKey(
        ContentType,
        SET_NULL,
        verbose_name=_("content type"),
        blank=True,
        null=True,
    )
    object_id = TextField(_("object id"), blank=True, null=True)
    # Translators: 'repr' means representation
    # (https://docs.python.org/library/functions.html#repr)
    object_repr = CharField(_("object repr"), max_length=200)
    action_flag = PositiveSmallIntegerField(
        _("action flag"), choices=ActionFlag.choices
    )
    # change_message is either a string or a JSON structure
    change_message = TextField(_("change message"), blank=True)
    is_admin = BooleanField(default=True)
    read_users = ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="read_history_logs"
    )

    objects = HistoryLogManager()

    class Meta:
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")
        ordering = ["-action_time"]

    def __repr__(self):
        return str(self.action_time)

    def __str__(self):
        if self.is_addition():
            return gettext("Added “%(object)s”.") % {"object": self.object_repr}
        elif self.is_change():
            return gettext("Changed “%(object)s” — %(changes)s") % {
                "object": self.object_repr,
                "changes": self.get_change_message(),
            }
        elif self.is_deletion():
            return gettext("Deleted “%(object)s.”") % {"object": self.object_repr}

        return gettext("LogEntry Object")

    def is_addition(self):
        return self.action_flag == ActionFlag.ADDITION

    def is_change(self):
        return self.action_flag == ActionFlag.CHANGE

    def is_deletion(self):
        return self.action_flag == ActionFlag.DELETION

    def get_change_message(self):
        """
        If self.change_message is a JSON structure, interpret it as a change
        string, properly translated.
        """
        if self.change_message and self.change_message[0] == "[":
            try:
                change_message = json.loads(self.change_message)
            except json.JSONDecodeError:
                return self.change_message
            messages = []
            for sub_message in change_message:
                if "added" in sub_message:
                    if sub_message["added"]:
                        sub_message["added"]["name"] = gettext(
                            sub_message["added"]["name"]
                        )
                        messages.append(
                            gettext("Added {name} “{object}”.").format(
                                **sub_message["added"]
                            )
                        )
                    else:
                        messages.append(gettext("Added."))

                elif "changed" in sub_message:
                    sub_message["changed"]["fields"] = get_text_list(
                        [
                            gettext(field_name)
                            for field_name in sub_message["changed"]["fields"]
                        ],
                        gettext("and"),
                    )
                    if "name" in sub_message["changed"]:
                        sub_message["changed"]["name"] = gettext(
                            sub_message["changed"]["name"]
                        )
                        messages.append(
                            gettext("Changed {fields} for {name} “{object}”.").format(
                                **sub_message["changed"]
                            )
                        )
                    else:
                        messages.append(
                            gettext("Changed {fields}.").format(
                                **sub_message["changed"]
                            )
                        )

                elif "deleted" in sub_message:
                    sub_message["deleted"]["name"] = gettext(
                        sub_message["deleted"]["name"]
                    )
                    messages.append(
                        gettext("Deleted {name} “{object}”.").format(
                            **sub_message["deleted"]
                        )
                    )

            change_message = " ".join(msg[0].upper() + msg[1:] for msg in messages)
            return change_message or gettext("No fields changed.")
        elif self.change_message != "":
            return self.change_message
        else:
            return self.get_action_flag_display()

    def get_edited_object(self):
        """Return the edited object represented by this log entry."""
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_admin_url(self):
        """
        Return the admin URL to edit the object represented by this log entry.
        """
        if self.content_type and self.object_id:
            url_name = "admin:%s_%s_change" % (
                self.content_type.app_label,
                self.content_type.model,
            )
            try:
                return reverse(url_name, args=(quote(self.object_id),))
            except NoReverseMatch:
                pass
        return None

    def is_read(self, user):
        return self.read_users.filter(pk=user.pk).exists()

    def read(self, user):
        self.read_users.add(user)
        self.save()
