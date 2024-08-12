from django.contrib import admin
from solo.admin import SingletonModelAdmin

from apps.coins.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(SingletonModelAdmin):
    fields = ("rate",)
