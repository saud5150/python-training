from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.template.loader import render_to_string
from smtplib import SMTPException, SMTPAuthenticationError
import logging
from rest_framework.views import exception_handler
from datetime import datetime

logger = logging.getLogger(__name__)

def send_registration_email(user, password):
    """
    Safely send a registration email with user credentials and role, using HTML template.
    Returns True if success, False if email could not be sent.
    """
    try:
        role = user.get_role_display()
        subject = f"Welcome to the Platform - {role} Registration Successful"
        from_email = None  # uses DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        # Render HTML and plain text versions
        context = {
            'user': user,
            'role': role,
            'password': password,
            'year': datetime.now().year,
        }
        html_content = render_to_string('registration_on_email.html', context)
        text_content = (
            f"Hi {user.name},\n\n"
            f"You have been registered as a {role}.\n\n"
            f"Here are your login credentials:\n"
            f"Email: {user.email}\n"
            f"Password: {password}\n\n"
            "Thank you,\nThe Team"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True

    except (SMTPAuthenticationError, SMTPException, BadHeaderError) as e:
        logger.exception(f"Email sending failed for {user.email}: {str(e)}")
        return False

    except Exception as e:
        logger.exception(f"Unexpected error during email sending: {str(e)}")
        return False