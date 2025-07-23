from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException, SMTPAuthenticationError
import logging
from rest_framework.views import exception_handler


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

