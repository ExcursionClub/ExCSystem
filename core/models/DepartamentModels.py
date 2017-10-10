from django.db import models
from django.core.mail import send_mail

from .MemberModels import Member, Staffer


class Departament(models.Model):
    """
    General class for a gear department

    A departament is an organizational entity that 'contains' all the gear needed for a certain category of
    trips/activities. Each department also has an STL (senior trip leader) in charge of maintaining all the gear in the
    department, and should be notified each time an issue arises.

    At the time of writing, the existing departments were:
        "Camping", "Backpacking", "Rock Climbing", "Skiing/Snowboarding", "Kayaking", "Paddleboarding",
        "Surfing", "Wetsuits", "Mountaineering", "Archery", "Paintballing", "Free Diving", "Off-Road"]
    """

    #: The title of this department
    title = models.CharField(max_length=20)

    #: A short description of the type of trips and gear this department contains
    description = models.TextField()

    #: The staffer (Senior Trip Leader) in charge of maintaining this department
    stls = models.ManyToManyField(Staffer, related_name="STLs_of")

    def notify_STL(self, title, message, *related_gear):
        """
        If something happens in this department that requires the attention of the STL, send them an email

        :param title: title of the email to send
        :param message: the message to send in the body of the email, describing the issue
        :param related_gear: if applicable, the list of gear that requires attention

        :return: None
        """

        department_email = "{}@excursionclubucsb.org".format(self.title)
        stl_emails = [staffer.exc_email for staffer in self.stls.all()]
        email_body = \
            "Hi {} STL! \n" \
            "\n" \
            "This is an automated message to let you know that:\n" \
            "{}" \
            "\n".format(title, message)
        for gear in related_gear:
            email_body += "    {}\n".format(gear)

        email_body += "From your dearest robot <3"

        send_mail(
            title,
            email_body,
            department_email,
            stl_emails,
            fail_silently=False,
        )

    # TODO: Add convenience email functions (that call notify_STL, but require fewer args) for: low supply, broken gear, missing

