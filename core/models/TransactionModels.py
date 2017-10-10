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
            ("Break",  "Set Broken"),
            ("Fix",    "Set Fixed")
        )
         ),
        ("Auto Updates", (
            ("Missing", "Gear Missing"),
            ("Expire",  "Gear Expiration"),
            )
         )
    ]

    #: The time at which this transaction was created - will be automatically set and cannot be changed
    timestamp = models.DateTimeField(auto_now_add=True)

    #: A string defining the type of transaction this is (see transaction types)
    type = models.CharField(max_length=20, choices=transaction_types)

    #: The piece of gear this transaction relates to: MUST EXIST
    gear = models.ForeignKey(Gear, null=False, on_delete=models.PROTECT)

    #: If this transaction relates to a member, that member should be referenced here
    member = models.ForeignKey(Member, null=True, on_delete=models.PROTECT)

    #: Either "System" or a String of the rfid of the person who authorized the transaction
    authorizer = models.CharField(max_length=10, null=False)

    #: Any additional notes to be saved about this transaction
    comments = models.TextField()

    def validate_auth(self):
        """
        Makes sure that the person who authorized the transaction is in fact authorized to do so
        The only options that should return true are "System" (for when the system is automatically changing the status
        of a piece of gear without oversight) or the rfid of a staffer as a string.
        """
        return self.authorizer == "System" or Member.objects.get(rfid=self.authorizer).is_staff()

