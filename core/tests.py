from django.test import TestCase

from .forms import MemberForms


class MemberFormTests(TestCase):
    def test_email_already_registered(self):
        # Add email to db
        # Try to add same email again
        # Should raise exception since pk should be email
        # TODO: Implement
        pass

    def test_american_phone_number_format(self):
        # TODO: Implement regex validation
        pass
