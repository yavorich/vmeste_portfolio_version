from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from collections import OrderedDict


class PageNumberSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("current_page", self.page.number),
                    (
                        "next_page",
                        self.page.next_page_number() if self.page.has_next() else None,
                    ),
                    (
                        "previous_page",
                        self.page.previous_page_number()
                        if self.page.has_previous()
                        else None,
                    ),
                    ("num_pages", self.page.paginator.num_pages),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{page_query_param}=4".format(
                        page_query_param=self.page_query_param
                    ),
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{page_query_param}=2".format(
                        page_query_param=self.page_query_param
                    ),
                },
                "current_page": {
                    "type": "integer",
                    "example": 5,
                },
                "next_page": {
                    "type": "integer",
                    "example": 6,
                },
                "previous_page": {
                    "type": "integer",
                    "example": 4,
                },
                "num_pages": {
                    "type": "integer",
                    "example": 7,
                },
                "results": schema,
            },
        }
