import os

from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator


from core.models.MemberModels import Member
from ExCSystem import settings


class ExcPasswordResetView(PasswordResetView):
    from_email = settings.MEMBERSHIP_EMAIL_HOST_USER

