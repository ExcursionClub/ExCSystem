import os

from django.core.mail.backends.smtp import EmailBackend


class ExcursionEmailBackend(EmailBackend):

    def __init__(self, *args, **kwargs):
        super(ExcursionEmailBackend, self).__init__(*args, **kwargs)
        self.email = os.environ.get('DEFAULT_EMAIL')
        self.password = os.environ.get('DEFAULT_EMAIL_PASSWORD')



