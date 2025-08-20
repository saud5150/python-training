import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import DatabaseError, IntegrityError
from http import HTTPStatus

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler for unified error responses.

    - Adds HTTP status code and description to response
    - Handles database errors with custom message
    - Logs server-side exceptions
    """
    # Use DRF's built-in handler to get standard error response
    response = exception_handler(exc, context)

    # If DRF already handled the exception, add status code and human message
    if response is not None:
        status_code = response.status_code
        try:
            human_message = HTTPStatus(status_code).phrase
        except Exception:
            human_message = 'Error'
        response.data['status_code'] = status_code
        response.data['message'] = human_message
        # Optionally, add the path or view for debugging:
        # response.data['path'] = context['request'].path
        return response

    # Custom handling for database or unexpected errors (unhandled by DRF)
    if isinstance(exc, (DatabaseError, IntegrityError)):
        logger.exception("Database error occurred:")
        return Response({
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "A server error occurred (database problem).",
            "detail": str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Fallback: Unhandled error (returns HTTP 500)
    logger.exception("Unhandled server error:", exc_info=exc)
    return Response({
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "Internal Server Error",
        "detail": str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# utils/query_counter.py
from django.db import connection
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

class QueryCounter:
    def __init__(self, description="Query analysis"):
        self.description = description
        self.initial_queries = 0
        self.start_time = 0
        
    def __enter__(self):
        self.initial_queries = len(connection.queries)
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        total_queries = len(connection.queries) - self.initial_queries
        total_time = end_time - self.start_time
        
        if settings.DEBUG and total_queries > 0:
            print(f"\n=== {self.description} ===")
            print(f"Queries executed: {total_queries}")
            print(f"Time taken: {total_time:.3f}s")
            
            # Show duplicate queries
            queries = connection.queries[self.initial_queries:]
            sql_counts = {}
            
            for query in queries:
                sql = query['sql']
                if sql in sql_counts:
                    sql_counts[sql] += 1
                else:
                    sql_counts[sql] = 1
            
            duplicates = {sql: count for sql, count in sql_counts.items() if count > 1}
            if duplicates:
                print(f"⚠️  DUPLICATE QUERIES DETECTED:")
                for sql, count in duplicates.items():
                    print(f"  - Executed {count} times: {sql[:100]}...")
            
            # Show all queries if there are many
            if total_queries > 5:
                print("All queries:")
                for i, query in enumerate(queries, 1):
                    print(f"  {i}. {query['sql'][:100]}... ({query['time']}s)")
                    
    @property 
    def count(self):
        return len(connection.queries) - self.initial_queries