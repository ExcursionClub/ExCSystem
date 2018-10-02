import os

from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.views import PasswordResetView

from ExCSystem import settings

class ExcursionEmailBackend(EmailBackend):

    def __init__(self, *args, **kwargs):
        super(ExcursionEmailBackend, self).__init__(*args, **kwargs)
        self.email = os.environ.get('DEFAULT_EMAIL')
        self.password = os.environ.get('DEFAULT_EMAIL_PASSWORD')


class ExcPasswordResetView(PasswordResetView):

    email_template_name = 'registration/exc_password_reset_email.html'
    from_email = settings.MEMBERSHIP_EMAIL_HOST_USER
    extra_email_context = {'web_base': settings.WEB_BASE, 'site_name': settings.SITE_NAME}


