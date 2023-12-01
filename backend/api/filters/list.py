from django_filters.rest_framework import Filter


class ListFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs
        self.lookup_expr = "in"
        values = value.split(",")
        return super(ListFilter, self).filter(qs, values)
