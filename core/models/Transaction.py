from django.db import models

from core.models.MemberModels import Member
from core.models.GearModels import Gear


class Transaction(models.Model):
    """
    Model that stores the data for every transaction, to allow better monitoring of the status of the whole system
    """

    transaction_types = [
        ("Rental", (
            ("CheckOut",  "Check Out"),
            ("CheckIn",   "Check In"),
            ("Inventory", "In Stock")
        )
         ),
        ("Admin Actions", (
            ("Create", "New Gear"),
            ("Delete", "Remove Gear"),
            ("ReTag",  "Change Tag"),
            ("Break",  "Set Broken")
        )
         ),
        ("Auto Updates", (
            ("Missing", "Gear Missing"),
            ("Expire", "Gear Expiration"),
            )
         )
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=transaction_types)
    gear = models.ForeignKey(Gear, null=False, on_delete=models.PROTECT)
    member = models.ForeignKey(Member, null=True, on_delete=models.PROTECT)
    authorizer = models.CharField(max_length=30)
    comments = models.TextField()




