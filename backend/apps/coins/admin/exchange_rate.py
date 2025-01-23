from django.contrib import admin
from solo.admin import SingletonModelAdmin

from apps.admin_history.admin import site
from apps.coins.models import ExchangeRate


@admin.register(ExchangeRate, site=site)
class ExchangeRateAdmin(SingletonModelAdmin):
    fields = ("rate",)
