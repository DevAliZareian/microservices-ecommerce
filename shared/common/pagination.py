"""
Standard pagination class used across all services.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .responses import paginated_response


class StandardPagination(PageNumberPagination):
    """
    Consistent pagination with configurable page size.
    Usage: Add to DRF settings or per-view.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """Override to use our standard response format."""
        return paginated_response(
            data=data,
            pagination={
                'count': self.page.paginator.count,
                'page': self.page.number,
                'page_size': self.page.paginator.per_page,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page_number': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page_number': self.page.previous_page_number() if self.page.has_previous() else None,
            }
        )