from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

from accounts.models import Subscriber


def detect_user_type(user):
    """Helper function for checking the role
       of the user and returns appropriate path."""
    if user.is_staff:
        return '/admin'
    else:
        return reverse('dashboard')


def send_verification_email(request, user, mail_subject, email_template):
    """Helper function for sending verification emails to newly registered users."""
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()


def send_confirmation_email(to_email, mail_subject, email_template):
    """Helper function for sending emails with confirmation,
       for example confirming changing the password."""
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template)
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()


def send_newsletter(title, content, email_template):
    """Helper function  for sending newsletter emails. Gets from_email
       and emails from all subscribers."""
    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = list(Subscriber.objects.all().values_list('email', flat=True))
    message = render_to_string(email_template, {
        'title': title,
        'content': content
    })
    mail = EmailMessage(title, message, from_email, to=to_emails)
    mail.send()
