from django.contrib import admin
from solo.admin import SingletonModelAdmin

from coins.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(SingletonModelAdmin):
    fields = ("rate",)
