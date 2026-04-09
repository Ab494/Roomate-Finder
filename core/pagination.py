# This file defines custom pagination classes for the Roommate Finder API.
# Pagination controls how large result sets are split into pages for API responses.

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Custom pagination class that provides detailed pagination metadata."""
    # Default number of items per page
    page_size = 20
    # Allow clients to specify custom page size via query parameter
    page_size_query_param = 'page_size'
    # Maximum allowed page size to prevent excessive data transfer
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return paginated response with enhanced metadata."""
        return Response({
            'count': self.page.paginator.count,        # Total number of items
            'next': self.get_next_link(),              # URL for next page
            'previous': self.get_previous_link(),      # URL for previous page
            'total_pages': self.page.paginator.num_pages,  # Total number of pages
            'results': data,                           # Actual data for this page
        })
