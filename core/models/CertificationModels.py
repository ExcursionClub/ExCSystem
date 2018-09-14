from django.db import models


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

