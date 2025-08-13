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
    serializer_class = None

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

    def send_successful_response(self, data=None, description="Success", serializer_class=None, many=None, payload=None, paginate=False, **serializer_kwargs):
        """
        Send a successful response with serialized data
        
        Args:
            data: The data to serialize (queryset, model instance, or already serialized data)
            description: Success message
            serializer_class: Serializer class to use (overrides self.serializer_class)
            many: Whether to serialize multiple objects
            payload: Alternative to data parameter
            paginate: Whether to apply pagination
            **serializer_kwargs: Additional kwargs for serializer
        """
        try:
            # Use payload if data is None (for backward compatibility)
            actual_data = data if data is not None else payload
            
            if actual_data is None:
                return Response({
                    "success": True,
                    "message": description,
                    "data": []
                }, status=status.HTTP_200_OK)
            
            # Use provided serializer_class or fall back to class attribute
            serializer_cls = serializer_class or self.serializer_class
            
            # Handle pagination if requested
            if paginate and hasattr(actual_data, 'model'):  # Check if it's a QuerySet
                page, paginator = self.paginate_queryset(actual_data)
                if page is not None:
                    if serializer_cls:
                        serializer = serializer_cls(page, many=True, **serializer_kwargs)
                        return paginator.get_paginated_response(serializer.data)
                    else:
                        return paginator.get_paginated_response(list(page))
            
            if serializer_cls is None:
                # If no serializer class is available, return data as-is
                return Response({
                    "success": True,
                    "message": description,
                    "data": actual_data
                }, status=status.HTTP_200_OK)
            
            # Determine if we need many=True based on data type
            if many is None:
                # Check if data is a QuerySet or list
                from django.db.models.query import QuerySet
                many = isinstance(actual_data, (QuerySet, list))
            
            # Serialize the data
            serializer = serializer_cls(actual_data, many=many, **serializer_kwargs)
            
            return Response({
                "success": True,
                "message": description,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return self.send_exception_response(e, "Error in send_successful_response")
    
    def send_201_response(self, data, description="Created successfully"):
        """
        Send a 201 Created response
        """
        return Response({
            "success": True,
            "message": description,
            "data": data
        }, status=status.HTTP_201_CREATED)
    
    def send_bad_response(self, errors, description="Bad request", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Send a bad request response
        """
        return Response({
            "success": False,
            "message": description,
            "errors": errors
        }, status=status_code)
    
    def send_no_content_response(self, description="Deleted successfully"):
        """
        Send a 204 No Content response
        """
        return Response({
            "success": True,
            "message": description
        }, status=status.HTTP_204_NO_CONTENT)
    
    def send_exception_response(self, exception, description="An error occurred"):
        """
        Send an exception response
        """
        import logging
        logging.error(f"Exception: {str(exception)}")
        
        return Response({
            "success": False,
            "message": description,
            "error": str(exception)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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