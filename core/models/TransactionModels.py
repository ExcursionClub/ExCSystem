from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from core.models.MemberModels import Member
from core.models.GearModels import Gear


def validate_auth(authorizer):
    """
    Makes sure that the person who authorized the transaction is in fact authorized to do so
    """

    # If the member is not a staffer, then they are not allowed to authorize a transaction like this
    if not authorizer.is_staff:
        raise ValidationError("{} is not allowed to authorize a transaction".format(authorizer.name))


def validate_available(gear):
    """Ensures that the piece of gear is in fact available for checkout in the system"""
    if not gear.is_available():
        raise ValidationError("This piece of gear [{}] is not available for checkout".format(gear.rfid))


def validate_required_certs(member, gear):
    """
    Validates that the member has the certifications required to check out this piece of gear

    :param member: member interested in checking out this piece of gear
    :param gear: piece of gear the member is trying to check out
    """
    has_all_perms = True
    for cert_required in gear.min_required_certs.all():
        if cert_required not in member.certifications.all():
            has_all_perms = False
    if not has_all_perms:
        raise ValidationError("The member does not have the certifications required to rent this piece of gear")


class TransactionManager(models.Manager):

    def __make_transaction(self, authorizer_rfid, type, gear, member=None, comments=""):
        """
        Basic transaction creation function, with the universal validators

        :param type: the type of the transaction
        :param gear: a gear model instance, the piece of gear that is being referred to
        :param authorizer: string, the rfid of the entity authorizing the transaction
        :param member: if applicable, the member referenced in the transaction (default=None)
        :param comments: any extra comments about the transaction (default="")
        :return: Transaction
        """
        authorizer = Member.objects.get(rfid=authorizer_rfid)
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

    def make_checkout(self, authorizer_rfid, gear_rfid, member_rfid, return_date):
        """
        Central function for creating checkout type transactions. This is the only way gear should be checked out

        :param gear_rfid: string, the 10-digit rfid of the gear being checked out
        :param member_rfid: string, the 10-digit rfid of the member checking out the gear
        :param authorizer_rfid: string, the 10-digit rfid of entity authorizing the transaction (should be staffer)
        :param return_date: the date by which the gear should be returned
        :return: transaction
        """
        # First, get the objects we are concerned with
        gear = Gear.objects.get(rfid=gear_rfid)
        member = Member.objects.get(rfid=member_rfid)

        # Run all the necessary validations
        validate_available(gear)
        validate_required_certs(member, gear)

        # If everything validated, we can try to make the transaction
        comment = "Return date = {}".format(return_date)
        transaction = self.__make_transaction(authorizer_rfid, "CheckOut", gear, member=member, comments=comment)

        # If the transaction was validated, then we can actually change the gear status
        gear.status = 1
        gear.checked_out_to = member
        gear.save()
        return transaction

    def add_gear(self, authorizer_rfid, gear_rfid, gear_name, gear_department, *required_certs):
        """
        Central function for creating Gear. This is the only way gear should ever be created

        :param authorizer_rfid: string, the 10-digit rfid of entity authorizing the transaction (should be staffer)\
        :param gear_rfid: string, the 10-digit rfid of the gear being checked out
        :param gear_name: string, the name of the piece of gear to be checked out
        :param gear_department: the department this gear belongs in
        :param required_certs: a list of the minimum certifications required to check this piece of gear out
        :return: Transaction (the transaction logging this gear addition), gear (the new piece of gear)
        """

        # Create the gear, because it is needed for creating the transaction
        gear = Gear(rfid=gear_rfid, name=gear_name, department=gear_department, status=0)
        gear.save()
        for cert in required_certs:
            gear.min_required_certs.add(cert)
        gear.save()

        # Make the transaction. This will also run all the necessary validations
        try:
            transaction = self.__make_transaction(authorizer_rfid, "Create", gear, comments="")
        # If any validation failed, we need to undo the gear creation before aborting
        except ValidationError:
            gear.delete()
            print("This was not a valid gear creation. No gear was created")
            raise

        # If everything went smoothly to this point, we can return the transaction logging the addition and the gear
        return transaction, gear

    def check_in_gear(self, authorizer_rfid, gear_rfid):
        """
        Central function for checking in gear. All gear check-ins must pass through here

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear being checked in
        :return: Check-in type Transaction
        """
        # First, retrieve the piece of gear we are concerned with
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "CheckIn", gear)

        # If the transaction went through, we can go ahead and check in the gear
        gear.status = 0
        gear.checked_out_to = None

        return transaction


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
    timestamp = models.DateTimeField(auto_now_add=True)

    #: A string defining the type of transaction this is (see transaction types)
    type = models.CharField(max_length=20, choices=transaction_types)

    #: The piece of gear this transaction relates to: MUST EXIST
    gear = models.ForeignKey(Gear, null=False, on_delete=models.PROTECT, related_name="has_checked_out",
                             validators=[validate_available])

    #: If this transaction relates to a member, that member should be referenced here
    member = models.ForeignKey(Member, null=True, on_delete=models.PROTECT)

    #: Either SYSTEM or a String of the rfid of the person who authorized the transaction
    authorizer = models.ForeignKey(Member, null=False, on_delete=models.PROTECT,
                                   related_name="has_authorized", validators=[validate_auth])

    #: Any additional notes to be saved about this transaction
    comments = models.TextField(default="")

    def __str__(self):
        return "{} Transaction for a {}".format(self.type, self.gear.name)

