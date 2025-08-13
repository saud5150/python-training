import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    """
    Standard pagination class following DRF best practices
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Custom response format to match BaseView style
        """
        return Response({
             'description': 'Data retrieved successfully',
            'payload': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                }
            }
        })

class BaseView(APIView):
    """
    Base view class for participation app with common response methods.
    """
    pagination_class = StandardPagination

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
    
    def paginate_queryset(self, queryset):
            """
            Return a single page of results, or `None` if pagination is disabled.
            """
            if self.paginator is None:
                return None, None
            
            page = self.paginator.paginate_queryset(queryset, self.request, view=self)
            if page is not None:
                return page, self.paginator
            return None, None

    def send_successful_response(self, payload, description="", status_code=status.HTTP_200_OK, queryset=None, serializer_class=None, paginate=False, **serializer_kwargs):
        """
        Send a successful response with data and optional description.
        
        Args:
            payload: The data to send in the response
            description: Optional description message
            status_code: HTTP status code (default: 200)
        
        Returns:
            Response object with data and status code
        """
# If queryset is provided, handle serialization and optional pagination
        if queryset is not None:
            if serializer_class is None:
                raise ValueError("serializer_class is required when queryset is provided")
            
            if paginate and self.pagination_class is not None:
                # Apply pagination
                page, paginator = self.paginate_queryset(queryset)
                
                if page is not None:
                    # Paginated response
                    serializer = serializer_class(page, many=True, **serializer_kwargs)
                    return paginator.get_paginated_response(serializer.data)
        # No pagination - serialize all data
        serializer = serializer_class(queryset, many=True, **serializer_kwargs)
        payload = serializer.data
        
        return Response({"description": description, "payload": payload}, status=status_code)
    
    def send_201_response(self, payload, description=""):
        """
        Send a 201 Created response with data and optional description.
        
        Args:
            payload: The data to send in the response
            description: Optional description message
        
        Returns:
            Response object with data and 201 status code
        """
        return Response({"description": description, "payload": payload}, status=status.HTTP_201_CREATED)
    
    def send_bad_response(self, errors, description="", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Send a bad request response with errors and optional description.
        
        Args:
            errors: The error data to send in the response
            description: Optional description message
            status_code: HTTP status code (default: 400)
        
        Returns:
            Response object with errors and status code
        """
        return Response({"description": description, "errors": errors}, status=status_code)
    
    def send_no_content_response(self):
        """
        Send a 204 No Content response.
        
        Returns:
            Response object with 204 status code
        """
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    def send_exception_response(self, exc, description="An error occurred", status_code=None):
        """
        Standardized error response for exceptions.

        Args:
            exc (Exception): The caught exception instance.
            description (str): Optional human-readable description.
            status_code (int): HTTP status code. Default to 500 if not provided.

        Returns:
            DRF Response with formatted error.
        """
        # log the exception here for debugging
        logging.error(f"Exception: {exc}", exc_info=True)

        if status_code is None:
            # Default to 500 internal server error if no specific status provided
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(
            {
                "description": description,
                "errors": str(exc),
            },
            status=status_code,
        )
    
    @staticmethod
    def get_pagination_openapi_parameters():
        """
        Return standard pagination parameters for OpenAPI documentation.
        
        Returns:
            list: List of OpenApiParameter objects for pagination
        """
        from drf_spectacular.utils import OpenApiParameter, OpenApiExample
        from drf_spectacular.types import OpenApiTypes
        
        return [
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number (starts from 1)',
                required=False,
                examples=[
                    OpenApiExample(name='first_page', summary='First page', value=1),
                    OpenApiExample(name='second_page', summary='Second page', value=2),
                ]
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of results per page (default: 20, max: 100)',
                required=False,
                examples=[
                    OpenApiExample(name='default_page_size', summary='Default page size', value=20),
                    OpenApiExample(name='larger_page_size', summary='Larger page size', value=50),
                    OpenApiExample(name='maximum_page_size', summary='Maximum page size', value=100),
                ]
            ),
        ]