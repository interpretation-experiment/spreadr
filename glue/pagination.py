from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageCountingPagination(PageNumberPagination):
    """Add a page_count field to normal PageNumberPagination."""

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'pages_count': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
