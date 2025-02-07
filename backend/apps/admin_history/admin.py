from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.views.main import PAGE_VAR
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from apps.admin_history.models import HistoryLog, ActionFlag
from apps.api.models import SupportRequestMessage
from core.utils.short_text import short_text


def bool_display(value: bool):
    if value is None:
        return "-"
    if value:
        return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
    else:
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')


def change_message_icon(action_flag, message):
    match action_flag:
        case ActionFlag.ADDITION:
            return mark_safe(f'<slug class="addlink"></slug>{message}')
        case ActionFlag.CHANGE:
            return mark_safe(f'<slug class="changelink"></slug>{message}')
        case ActionFlag.DELETION:
            return mark_safe(f'<slug class="deletelink"</slug>{message}')
    return message


class HistoryAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        app_list = self.get_app_list(request)
        for app in app_list:
            for model_dict in app["models"]:
                model = model_dict["model"]
                content_type = get_content_type_for_model(model)
                model_dict.update(
                    {
                        "has_user_history": HistoryLog.objects.filter(
                            content_type=content_type, is_admin=False
                        ).exists(),
                        "history_user_url": reverse(
                            "admin:history_user_%s_%s"
                            % (model._meta.app_label, model._meta.model_name)
                        ),
                        "history_user_notify_count": HistoryLog.objects.filter(
                            content_type=content_type, is_admin=False
                        )
                        .exclude(read_users__id=request.user.id)
                        .count(),
                        "has_admin_history": HistoryLog.objects.filter(
                            content_type=content_type, is_admin=True
                        ).exists(),
                        "history_admin_url": reverse(
                            "admin:history_admin_%s_%s"
                            % (model._meta.app_label, model._meta.model_name)
                        ),
                        "history_admin_notify_count": HistoryLog.objects.filter(
                            content_type=content_type, is_admin=True
                        )
                        .exclude(read_users__id=request.user.id)
                        .count(),
                    }
                )
            app["has_user_history"] = any(
                (model_dict["has_user_history"] for model_dict in app["models"])
            )
            app["has_admin_history"] = any(
                (model_dict["has_admin_history"] for model_dict in app["models"])
            )

        extra_context.update(
            {
                "app_list": app_list,
                "has_user_history": any((app["has_user_history"] for app in app_list)),
                "has_admin_history": any(
                    (app["has_admin_history"] for app in app_list)
                ),
            }
        )
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urlpatterns = super().get_urls()

        custom_urls = []
        for model in self._registry.keys():
            custom_urls += [
                path(
                    "history_admin/%s/%s/"
                    % (model._meta.app_label, model._meta.model_name),
                    self.admin_view(self.history_view(model, is_admin=True)),
                    name="history_admin_%s_%s"
                    % (model._meta.app_label, model._meta.model_name),
                ),
                path(
                    "history_user/%s/%s/"
                    % (model._meta.app_label, model._meta.model_name),
                    self.admin_view(self.history_view(model, is_admin=False)),
                    name="history_user_%s_%s"
                    % (model._meta.app_label, model._meta.model_name),
                ),
            ]

        return custom_urls + urlpatterns

    def history_view(self, model, is_admin):
        additional_cols = (
            model._meta.history_fields if hasattr(model._meta, "history_fields") else {}
        )
        if not is_admin and isinstance(model(), SupportRequestMessage):
            additional_cols.pop("author_user", None)

        col_headers = (
            [_("Date/time"), f"ID Объекта", "Объект"]
            + list(additional_cols.values())
            + [_("User"), _("Action"), "Новое действие"]
        )

        def _history_view(request):
            action_list = HistoryLog.objects.filter(
                content_type=get_content_type_for_model(model), is_admin=is_admin
            ).order_by("-action_time")

            paginator = Paginator(action_list, 100)
            page_number = request.GET.get(PAGE_VAR, 1)
            page_obj = paginator.get_page(page_number)
            page_range = paginator.get_elided_page_range(page_obj.number)

            for obj in page_obj.object_list:
                is_new = not obj.is_read(request.user)
                obj.read(request.user)
                obj.display_values = (
                    [
                        obj.action_time.strftime("%d/%m/%yг. %H:%M"),
                        obj.object_id,
                        obj.object_repr,
                    ]
                    + [
                        short_text(obj.object_data.get(field, "-"), 30)
                        for field in additional_cols.keys()
                    ]
                    + [
                        f"{obj.user_id}. "
                        + f"{obj.user.get_full_name()} {obj.user.phone_number}".lstrip()
                        if obj.user is not None
                        else "-",
                        change_message_icon(obj.action_flag, obj.get_change_message()),
                        bool_display(is_new),
                    ]
                )

            history_label_suffix = "администратора" if is_admin else "пользователя"
            context = {
                **self.each_context(request),
                "history_label": f"История {history_label_suffix}",
                "opts": model._meta,
                "module_name": str(capfirst(model._meta.verbose_name_plural)),
                "action_list": page_obj,
                "pagination_required": paginator.count > 100,
                "page_range": page_range,
                "page_var": PAGE_VAR,
                "col_headers": col_headers,
            }
            return TemplateResponse(request, "admin_history.html", context)

        return _history_view


site = HistoryAdminSite()
