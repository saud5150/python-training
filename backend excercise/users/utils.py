from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException, SMTPAuthenticationError
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import DatabaseError, IntegrityError
from http import HTTPStatus

logger = logging.getLogger(__name__)

def send_registration_email(user, password):
    """
    Safely send a registration email with user credentials and role.
    Returns True if success, False if email could not be sent.
    """
    try:
        role = user.get_role_display()
        subject = f"Welcome to the Platform - {role} Registration Successful"
        message = (
            f"Hi {user.name},\n\n"
            f"You have been registered as a {role}.\n\n"
            f"Here are your login credentials:\n"
            f"Email: {user.email}\n"
            f"Password: {password}\n\n"
            "Thank you,\nThe Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=False
        )

        return True

    except (SMTPAuthenticationError, SMTPException, BadHeaderError) as e:
        logger.exception(f"Email sending failed for {user.email}: {str(e)}")
        return False

    except Exception as e:
        logger.exception(f"Unexpected error during email sending: {str(e)}")
        return False

# users/utils.py (or api/utils.py)


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
