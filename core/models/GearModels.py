from django.db import models
from .MemberModels import Member
from .DepartmentModels import Department
from .CertificationModels import Certification


# TODO: subclass Gear for all the different types of gear
# TODO: figure out how to "subclass" via the django admin, so a new type of gear could be added if necessary

class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    class Meta:
        verbose_name_plural = "Gear"

    rfid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    status_choices = [
        (0, "In Stock"),        # Ready and available in the gear sheds, waiting to be used
        (1, "Checked Out"),     # Somebody has it right now, but it should soon be available again
        (2, "Broken"),          # It is broken to the point it should not be checked out, waiting for repair
        (3, "Missing"),         # Has been checked out for a while, time to yell at a member to give it back
        (4, "Dormant"),         # Missing for very long time: assume it has been lost until found
        (5, "Removed"),         # It is gone, dead and never coming back. Always set manually
    ]
    #: The status determines what transactions the gear can participate in and where it is visible
    status = models.IntegerField(choices=status_choices)

    #: The department to which this gear belongs (roughly corresponds to STL positions)
    department = models.ForeignKey(Department)

    #: All the certifications that a member must posses to be allowed to check out this gear
    min_required_certs = models.ManyToManyField(Certification, verbose_name="Minimal Certifications Required for Rental")

    #: Who currently has this piece of gear. If null, then the gear is not checked out
    checked_out_to = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL)

    #: The date at which this gear is due to be returned, null if not checked out
    due_date = models.DateField(null=True, default=None)

    # TODO: Add image of gear

    def __str__(self):
        return self.name

    def is_available(self):
        """Returns True if the gear is available for renting"""
        if self.status == 0:
            return True
        else:
            return False

    def is_active(self):
        """Returns True if the gear is actively in circulation (ie could be checked out in a few days)"""
        if self.status <= 1:
            return True
        else:
            return False

    def is_existent(self):
        """Returns True if the gear has not been removed or lost"""
        if self.status <= 3:
            return True
        else:
            return False

