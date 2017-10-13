from django.db import models
from django.core.exceptions import ValidationError

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


def validate_rfid(rfid):
    """Ensures that the given rfid is unique"""
    # TODO: is there a better way to do this? This approach might get slow
    member_rfids = [member.rfid for member in Member.objects.all()]
    if rfid in member_rfids:
        raise ValidationError("This rfid is already in use by the member {}".format(Member.objects.get(rfid=rfid)))
    else:
        # Do this in a two step process to reduce processing time in half of cases
        gear_rfids = [gear.rfid for gear in Gear.objects.all()]
        if rfid in gear_rfids:
            raise ValidationError("This rfid is already in use by a {}".format(Gear.objects.get(rfid=rfid)))
    # TODO: If we add other kinds of RFID tags, make sure this is updated


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
        :param gear_rfid: string, the 10-digit rfid of the gear being added
        :param gear_name: string, the name of the piece of gear to be checked out
        :param gear_department: the department this gear belongs in
        :param required_certs: a list of the minimum certifications required to check this piece of gear out
        :return: Transaction (the transaction logging this gear addition), gear (the new piece of gear)
        """
        # First must make sure that the rfid is not in use by anything
        validate_rfid(gear_rfid)

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

    def retag_gear(self, authorizer_rfid, old_rfid, new_rfid):
        """
        Central function to change the rfid of a piece of gear

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param old_rfid: string, the old 10-digit rfid of the piece of gear
        :param new_rfid: string, the new 10-digit rfid to give this piece of gear
        :return: ReTag Transaction
        """
        validate_rfid(new_rfid)
        gear = Gear.objects.get(rfid=old_rfid)

        # Create a transaction to ensure everything is authorized
        details = "Changed RFID from {} to {}".format(old_rfid, new_rfid)
        transaction = self.__make_transaction(authorizer_rfid, "ReTag", gear, comments=details)

        # If the transaction went through, we can go ahead and remove the gear
        gear.rfid = new_rfid
        gear.save()

        return transaction

    def fix_gear(self, authorizer_rfid, gear_rfid, repairs_description):
        """
        Central function for noting that a piece of gear was repaired

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :param repairs_description: a description of the repairs that were made
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "Fix", gear, comments=repairs_description)

        gear.set_status = 0
        gear.save()
        return transaction

    def break_gear(self, authorizer_rfid, gear_rfid, damage_description):
        """
        Central function for noting damage to gear

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :param damage_description: a description of the damage and (if known) repairs needed
        :return: Break Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "Break", gear, comments=damage_description)

        gear.set_status = 2
        gear.save()

        return transaction

    def missing_gear(self, authorizer_rfid, gear_rfid):
        """
        Central function for noting that a piece of gear has been missing for a while

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)
        last_owner = gear.checked_out_to.get_full_name()
        details = "Last known owner: {}".format(last_owner)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "Fix", gear, comments=details)

        gear.set_status = 3
        gear.save()
        return transaction

    def expire_gear(self, authorizer_rfid, gear_rfid):
        """
        Central function for noting that a piece of gear is probably lost

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)
        last_owner = gear.checked_out_to.get_full_name()
        details = "Last known owner: {}".format(last_owner)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "Fix", gear, comments=details)

        gear.set_status = 4
        gear.save()
        return transaction

    def delete_gear(self, authorizer_rfid, gear_rfid, reason):
        """
        Central function for permanently removing a gear from circulation

        This should only be used when a piece of gear is being throw away. Since this is a dramatic action, the STL
        for the relevant department should get an email notifying them of the removal, in case it was not intentional

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear being deleted
        :param reason: string explaining why this piece of gear is being removed
        :return: transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(authorizer_rfid, "Delete", gear, comments=reason)

        # If the transaction went through, we can go ahead and remove the gear
        gear.status = 5
        gear.checked_out_to = None
        gear.department.notify_gear_removed()

        return transaction

    def override(self, authorizer_rfid, gear_rfid, **kwargs):
        """
        Allows the admin to override the settings on any piece of gear

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear being deleted

        available kwargs:
            rfid: (default None), the rfid to set the rfid to. If left None, no change is made
            status: (default None), the status to set the gear to. If left None, no change is made
            department: (default None), the department to set the gear into. If left None, no change is made
            checked_out_to: (default None), the member to check the gear out to. If left None, no change is made
            min_required_certs: (default None), A list of all the certs to require. If left None, no change is made

        :return: Admin Override Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        if authorizer_rfid != "0000000000":
            raise ValidationError("You can't do admin overrides unless you know the admin code")

        # All the changes made will be described here
        action = "Admin override on {} [{}]: \n".format(gear, gear_rfid)

        # Set each of the available kwargs to their desired value if they are not none
        for kwarg in kwargs.keys():
            value = kwargs[kwarg]
            old_value = gear.__getattribute__(kwarg)
            gear.__setattr__(kwarg, value)
            action += "  Changed {} from {} to {}\n".format(kwarg, old_value, value)

        # Save the changes made in a transaction
        transaction = self.__make_transaction(authorizer_rfid, "Delete", gear, comments=action)
        return transaction


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
            ("Create",   "New Gear"),
            ("Delete",   "Remove Gear"),
            ("ReTag",    "Change Tag"),
            ("Break",    "Set Broken"),
            ("Fix",      "Set Fixed"),
            ("Override", "Admin Override")
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

