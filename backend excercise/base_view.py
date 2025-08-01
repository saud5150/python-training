import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class BaseView(APIView):
    """
    Base view class for participation app with common response methods.
    """
    
    def send_successful_response(self, payload, description="", status_code=status.HTTP_200_OK):
        """
        Send a successful response with data and optional description.
        
        Args:
            payload: The data to send in the response
            description: Optional description message
            status_code: HTTP status code (default: 200)
        
        Returns:
            Response object with data and status code
        """
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