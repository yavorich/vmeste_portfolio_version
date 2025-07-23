from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ChoiceField

from apps.admin_history.admin import site
from apps.api.models import Theme, Category


class CategoryInline(admin.TabularInline):
    model = Category


class ThemeForm(ModelForm):
    payment_type = ChoiceField(
        label="Тип оплаты",
        choices=Theme.PaymentType.choices,
        widget=AdminRadioSelect(),
    )

    def clean(self):
        cleaned_data = super().clean()
        match cleaned_data.get("payment_type"):
            case Theme.PaymentType.FREE:
                cleaned_data["commission_percent"] = None
                cleaned_data["price"] = None

            case Theme.PaymentType.MASTER:
                if cleaned_data.get("price") is None:
                    raise ValidationError(
                        {"price": "Должна быть указана стоимость для организатора"}
                    )

                cleaned_data["commission_percent"] = None

            case Theme.PaymentType.PROF:
                if cleaned_data.get("commission_percent") is None:
                    raise ValidationError(
                        {"commission_percent": "Должна быть указана комиссия сервиса"}
                    )

                cleaned_data["price"] = None

            case _:
                raise ValidationError("Должен быть указан тип")

        return cleaned_data


@admin.register(Theme, site=site)
class ThemeAdmin(admin.ModelAdmin):
    change_form_template = "theme/change_form.html"
    inlines = [CategoryInline]
    form = ThemeForm
    list_display = ["title", "events_count", "commission_percent", "price"]

    @admin.display(description="Кол-во событий")
    def events_count(self, obj):
        return obj.events.count()
