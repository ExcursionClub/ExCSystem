from django.db import models
from django.core.exceptions import ValidationError

from core.models.MemberModels import Member
from core.models.GearModels import Gear


def validate_auth(authorizer):
    """
    Makes sure that the person who authorized the transaction is in fact authorized to do so
    The only options that should return true are "System" (for when the system is automatically changing the status
    of a piece of gear without oversight) or the rfid of a staffer as a string.
    """
    if not (authorizer == "System" or Member.objects.get(rfid=authorizer).is_staff()):
        raise ValidationError("The entity [{}] is not allowed to authorize a transaction".format(authorizer))


def validate_available(gear_pk):
    """Ensures that the piece of gear is in fact available for checkout in the system"""
    if not Gear.objects.get(pk=gear_pk).status == 0:
        raise ValidationError("This piece of gear [{}] is not available for checkout".format(gear.rfid))


def validate_required_certs(member, gear):
    """
    Validates that the member has the certifications required to check out this piece of gear

    :param member: member interested in checking out this piece of gear
    :param gear: piece of gear the member is trying to check out
    """
    has_all_perms = True
    for cert_required in gear.min_required_certs:
        if cert_required not in member.certifications:
            has_all_perms = False
    if not has_all_perms:
        raise ValidationError("The member does not have the certifications required to rent this piece of gear")


class TransactionManager(models.Manager):

    def __make_transaction(self, type, gear, authorizer, member=None, comments=""):
        """
        Basic transaction creation function, with the universal validators

        :param type: the type of the transaction
        :param gear: a gear model instance, the peice of gear that is being referred to
        :param authorizer: string identifying the entity authorizing the transaction
        :param member: if applicable, the member referenced in the transaction (default=None)
        :param comments: any extra comments about the transaction (default="")
        :return: Transaction
        """
        validate_auth(authorizer)

        transaction = self.model(
            type=type,
            gear=gear,
            member=member,
            authorizer=authorizer,
            comments=comments
        )
        transaction.save(using=self._db)
        return transaction

    def make_checkout(self, gear_rfid, member_rfid, authorizer, return_date):
        """
        Convenience function for creating checkout type transactions

        :param gear_rfid: string containing the rfid of the gear being checked out
        :param member_rfid: string containing the rfid of the member checking out the gear
        :param authorizer: string of entity authorizing the transaction (should be staffer0
        :param duration: the date by which the gear should be returned
        :return: transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)
        member = Member.objects.get(rfid=member_rfid)
        comment = "Return date = {}".format(return_date)

        validate_available(gear)
        validate_required_certs(member, gear)

        self.__make_transaction("CheckOut", gear=gear, member=member, authorizer=authorizer, comments=comment)

    # TODO: make convenience functions for each transaction type


class Transaction(models.Model):
    """
    Model that stores the data for every transaction, to allow better monitoring of the status of the whole system

    NEVER CREATE TRANSACTIONS MANUALLY, ALWAYS USE THE MANAGER FUNCTIONS
    """

    objects = TransactionManager()

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
    timestamp = models.DateTimeField()

    #: A string defining the type of transaction this is (see transaction types)
    type = models.CharField(max_length=20, choices=transaction_types)

    #: The piece of gear this transaction relates to: MUST EXIST
    gear = models.ForeignKey(Gear, null=False, on_delete=models.PROTECT, validators=[validate_available])

    #: If this transaction relates to a member, that member should be referenced here
    member = models.ForeignKey(Member, null=True, on_delete=models.PROTECT)

    #: Either "System" or a String of the rfid of the person who authorized the transaction
    authorizer = models.CharField(max_length=10, null=False, validators=[validate_auth])

    #: Any additional notes to be saved about this transaction
    comments = models.TextField(default="")

    def __str__(self):
        return "{} Transaction for a {}".format(self.type, self.gear.name)


