import os

from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator


from core.models.MemberModels import Member
from ExCSystem import settings


class ExcursionEmailBackend(EmailBackend):

    def __init__(self, *args, **kwargs):
        super(ExcursionEmailBackend, self).__init__(*args, **kwargs)
        self.email = os.environ.get('DEFAULT_EMAIL')
        self.password = os.environ.get('DEFAULT_EMAIL_PASSWORD')


class ExcPasswordResetForm(PasswordResetForm):

    def get_users(self, email):
        """
        Get all the users with this email (should always be one or None)
        """
        active_users = Member.objects.filter(email__iexact=email)
        return (u for u in active_users if u.has_usable_password())

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # The domain is everything that comes after the '//' in the web base
        context['domain'] = settings.WEB_BASE.split('//')[1]
        context['site_name'] = 'Excursion Admin'
        super(ExcPasswordResetForm, self).send_mail(
            subject_template_name, email_template_name, context, from_email,
            to_email, html_email_template_name=html_email_template_name
        )


class ExcPasswordResetView(PasswordResetView):

    form_class = ExcPasswordResetForm
    from_email = settings.MEMBERSHIP_EMAIL_HOST_USER

