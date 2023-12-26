from enum import Enum
from django.db import models
from elasticsearch_dsl import Q
from django.utils.timezone import now, timedelta
from operator import ior, iand
from functools import reduce


class FilterName(models.TextChoices):
    TODAY = "today", "Сегодня"
    TOMORROW = "tomorrow", "Завтра"
    MY_CITY = "my_city", "Мой город"


class FilterGroup(str, Enum):
    DATE = "date"
    CITY = "city"


class EventFastFilterQuerySet(models.QuerySet):
    def get_filter_query(self, filter_ids, user):
        filter_queries = {
            FilterName.TODAY: Q("term", **{"date": now().date()}),
            FilterName.TOMORROW: Q(
                "term", **{"date": now().date() + timedelta(days=1)}
            ),
            FilterName.MY_CITY: Q("term", **{"city.id": user.city.id})
            if hasattr(getattr(user, "city", None), "id")
            else Q(),
        }
        filters = self.filter(id__in=filter_ids, is_active=True)
        group_queries = []
        for group in FilterGroup:
            group_filters = [f for f in filters if f.group == group]
            queries = [filter_queries[f.name] for f in group_filters]
            if queries:
                group_queries.append(reduce(ior, queries))
        return reduce(iand, group_queries)


class EventFastFilter(models.Model):
    name = models.CharField(max_length=8, choices=FilterName.choices, unique=True)
    is_active = models.BooleanField()

    @property
    def title(self):
        return FilterName(self.name).label

    @property
    def group(self):
        groups = {
            FilterName.TODAY: FilterGroup.DATE,
            FilterName.TOMORROW: FilterGroup.DATE,
            FilterName.MY_CITY: FilterGroup.CITY,
        }
        return groups[self.name].value

    objects = EventFastFilterQuerySet.as_manager()
