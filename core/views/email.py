import os

from core.models.MemberModels import Member
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.core.mail.backends.smtp import EmailBackend
from uwccsystem import settings


class ExcPasswordResetView(PasswordResetView):
    from_email = settings.MEMBERSHIP_EMAIL
