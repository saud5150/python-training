import logging
import hashlib
import json
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.conf import settings

from utils import QueryCounter

logger = logging.getLogger(__name__)


# # Cache utilities directly in base_view.py for minimal dependencies
# class CacheManager:
#     """Utility class for cache management operations"""
    
#     @staticmethod
#     def is_cache_healthy():
#         """Check if cache backend is available and healthy"""
#         try:
#             cache.set('health_check', 'ok', timeout=10)
#             return cache.get('health_check') == 'ok'
#         except Exception as e:
#             logger.warning(f"Cache health check failed: {e}")
#             return False
    
#     @staticmethod
#     def get_cache_key(request, prefix="api", include_user=True, include_params=True):
#         """Generate cache key for request"""
#         key_parts = [prefix]
        
#         # Add path info
#         path_key = request.path.replace('/', '_').replace('-', '_')
#         key_parts.append(path_key)
        
#         # Add user info if requested
#         if include_user and hasattr(request, 'user') and request.user.is_authenticated:
#             try:
#                 user_identifier = str(request.user.pk)
#                 key_parts.append(f"user_{user_identifier}")
#             except Exception as e:
#                 logger.warning(f"Could not get user ID for cache key: {e}")
#                 key_parts.append("user_authenticated")
        
#         # Add query parameters if requested
#         if include_params and request.GET:
#             try:
#                 params_str = "&".join([f"{k}={v}" for k, v in sorted(request.GET.items())])
#                 params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
#                 key_parts.append(f"params_{params_hash}")
#             except Exception as e:
#                 logger.warning(f"Could not process query params for cache key: {e}")
        
#         return ":".join(key_parts)
    
# def cache_api_response(ttl_type='DEFAULT', user_specific=True, cache_anonymous=False):
#     """
#     Decorator for caching API responses
    
#     Args:
#         ttl_type: Type of TTL to use ('SHORT', 'MEDIUM', 'LONG', 'DEFAULT')
#         user_specific: Whether to include user ID in cache key
#         cache_anonymous: Whether to cache responses for anonymous users
#     """
#     def decorator(func):
#         @wraps(func)
#         def wrapper(self, request, *args, **kwargs):
#             # Skip caching for non-GET requests
#             if request.method != 'GET':
#                 return func(self, request, *args, **kwargs)
            
#             # Skip caching for anonymous users if not allowed
#             if not cache_anonymous and not (hasattr(request, 'user') and request.user.is_authenticated):
#                 return func(self, request, *args, **kwargs)
            
#             # Generate cache key
#             cache_key = CacheManager.get_cache_key(
#                 request, 
#                 prefix=f"{self.__class__.__name__.lower()}",
#                 include_user=user_specific,
#                 include_params=True
#             )
            
#             # Try to get cached response
#             cached_response = cache.get(cache_key)
#             if cached_response is not None:
#                 logger.debug(f"Cache hit for key: {cache_key}")
#                 return Response(cached_response)
            
#             # Get fresh response
#             response = func(self, request, *args, **kwargs)
            
#             # Cache successful responses only
#             if response.status_code == 200:
#                 ttl = CacheManager.get_ttl(ttl_type)
#                 cache.set(cache_key, response.data, timeout=ttl)
#                 logger.debug(f"Cached response for key: {cache_key}, TTL: {ttl}")
            
#             return response
#         return wrapper
#     return decorator


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

    # Cache configuration (override in subclasses if needed)
    cache_ttl_type = 'DEFAULT'
    cache_user_specific = True
    cache_anonymous = False
    enable_caching = True
    
    # Query optimization settings (override in subclasses)
    select_related_fields = []     # ['user', 'category', 'quiz']
    prefetch_related_fields = []   # ['tags', 'participants']
    auto_optimize_queries = True   # Enable automatic query optimization
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add query counting to all HTTP methods"""
        method_name = request.method.lower()
        description = f"{self.__class__.__name__}.{method_name}"
        
        with QueryCounter(description):
            return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Optimized caching - check cache FIRST"""
        
        # Quick cache check first (no expensive operations)
        if getattr(self, 'enable_caching', True):
            cache_key = self._get_simple_cache_key(request)
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)  # Instant return!
        
        # Only do expensive operations if cache miss
        response = self._get_implementation(request, *args, **kwargs)
        
        # Cache the result
        if getattr(self, 'enable_caching', True) and response.status_code == 200:
            cache.set(cache_key, response.data, timeout=300)
        
        return response

    def _get_simple_cache_key(self, request):
        """Simple cache key generation without expensive operations"""
        import hashlib
        key_parts = [
            self.__class__.__name__,
            request.path,
            request.GET.urlencode() if request.GET else '',
            str(request.user.pk) if request.user.is_authenticated else 'anon'
        ]
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
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
            actual_data = data if data is not None else payload

            if actual_data is None:
                return Response({
                    "success": True,
                    "message": description,
                    "data": []
                }, status=status.HTTP_200_OK)

            from django.db.models.query import QuerySet

            # Determine 'many' based on data type if not explicitly provided
            if many is None:
                many = isinstance(actual_data, (list, QuerySet))

            if serializer_class:
                # Optimize queryset BEFORE serialization (if you have such method)
                if hasattr(actual_data, 'model') and hasattr(actual_data, 'select_related'):
                    actual_data = self._optimize_queryset(actual_data)

                # Apply pagination BEFORE serialization to reduce data size
                if paginate and many:
                    paginator = self.pagination_class()
                    page = paginator.paginate_queryset(actual_data, getattr(self, 'request', None))
                    if page is not None:
                        serializer = serializer_class(page, many=True, **serializer_kwargs)
                        return paginator.get_paginated_response(serializer.data)

                # Use only() for specific fields if possible
                if hasattr(serializer_class.Meta, 'fields') and hasattr(actual_data, 'only'):
                    if serializer_class.Meta.fields != '__all__':
                        actual_data = actual_data.only(*serializer_class.Meta.fields)

                serializer = serializer_class(actual_data, many=many, **serializer_kwargs)
                serialized_data = serializer.data
            else:
                serialized_data = actual_data

            return Response({
                "success": True,
                "message": description,
                "data": serialized_data,
                "count": len(serialized_data) if many and isinstance(serialized_data, list) else None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return self.send_exception_response(e, "Error processing response")


    def _optimize_queryset(self, queryset):
        """Apply query optimizations"""
        # Add select_related for foreign keys
        select_fields = getattr(self, 'select_related_fields', [])
        if select_fields:
            queryset = queryset.select_related(*select_fields)
        
        # Add prefetch_related for many-to-many
        prefetch_fields = getattr(self, 'prefetch_related_fields', [])
        if prefetch_fields:
            queryset = queryset.prefetch_related(*prefetch_fields)
        
        return queryset
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
    
    # def get_optimized_queryset(self, queryset=None):
    #     """
    #     Automatically optimize queryset with select_related and prefetch_related
    #     """
    #     if not getattr(self, 'auto_optimize_queries', True):
    #         return queryset
        
    #     if queryset is None:
    #         # Try to get queryset from model or serializer
    #         if hasattr(self, 'get_queryset'):
    #             queryset = self.get_queryset()
    #         elif hasattr(self, 'serializer_class') and hasattr(self.serializer_class.Meta, 'model'):
    #             queryset = self.serializer_class.Meta.model.objects.all()
    #         else:
    #             return queryset
        
    #     # Apply select_related for foreign keys
    #     select_fields = getattr(self, 'select_related_fields', [])
    #     if select_fields:
    #         queryset = queryset.select_related(*select_fields)
        
    #     # Apply prefetch_related for many-to-many/reverse foreign keys
    #     prefetch_fields = getattr(self, 'prefetch_related_fields', [])
    #     if prefetch_fields:
    #         queryset = queryset.prefetch_related(*prefetch_fields)
        
    #     return queryset
    