from django.db import models
from django.urls import reverse
from uwccsystem.settings import WEB_BASE


class Certification(models.Model):
    """
    General class for all types of certifications for renting gear or going on trips

    At the time of writing, the available certifications were:
        "SUP", "Kayaking", "Mountaineering", "Climbing"
    """

    #: The name of this certification
    title = models.CharField(max_length=140)

    #: Description of the minimum requirements needed to have this certification
    requirements = models.TextField(verbose_name="Minimum Certification Requirements")

    def __str__(self):
        return "{} Certification".format(self.title)

    def get_page_url(self):
        return WEB_BASE + reverse(
            "admin:core_certification_detail", kwargs={"pk": self.pk}
        )
