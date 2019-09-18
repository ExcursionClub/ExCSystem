from django.core.mail import send_mail
from django.db import models

from .MemberModels import Member, Staffer


class Department(models.Model):
    """
    General class for a gear department

    A departament is an organizational entity that 'contains' all the gear needed for a certain category of
    trips/activities. Each department also has an STL (senior trip leader) in charge of maintaining all the gear in the
    department, and should be notified each time an issue arises.

    At the time of writing, the existing departments were:
        "Camping", "Backpacking", "Rock Climbing", "Skiing/Snowboarding", "Kayaking", "Paddleboarding",
        "Surfing", "Wetsuits", "Mountaineering", "Archery", "Paintballing", "Free Diving", "Off-Road"]
    """

    #: The name of this department
    name = models.CharField(max_length=20)

    #: A short description of the type of trips and gear this department contains
    description = models.TextField()

    #: The staffer (Senior Trip Leader) in charge of maintaining this department
    stls = models.ManyToManyField(Staffer, related_name="STLs_of")

    def __str__(self):
        """Allows the department to be easily readable"""
        return self.name

    @property
    def stl_names(self):
        """Gets a list of all of the names of the STLs for this department"""
        return [stl.member.get_full_name() for stl in self.stls.all()]

    def notify_STL(self, title, message, *related_gear):
        """
        If something happens in this department that requires the attention of the STL, send them an email

        :param title: title of the email to send
        :param message: the message to send in the body of the email, describing the issue
        :param related_gear: if applicable, the list of gear that requires attention

        :return: None
        """

        department_email = "{}@climbingclubuw.org".format(self.name)
        stl_emails = [staffer.exc_email for staffer in self.stls.all()]
        email_body = (
            "Hi {} STL! \n"
            "\n"
            "This is an automated message to let you know that:\n"
            "{}"
            "\n".format(self.name, message)
        )
        for gear in related_gear:
            email_body += "    {}\n".format(gear)

        email_body += "From your dearest robot <3"

        send_mail(title, email_body, department_email, stl_emails, fail_silently=False)

    def notify_gear_removed(self, gear):
        """Sends an email to the STL that the piece of gear has been removed"""
        message = (
            "The following piece of gear has been permanently removed from circulation!"
        )
        self.notify_STL("Gear Removal", message, gear)

    # TODO: Add convenience email functions (that call notify_STL, but require fewer args) for: low supply, broken gear, gear gone missing
