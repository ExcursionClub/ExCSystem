import json
import logging

from datetime import date
from core.convinience import get_all_rfids
from core.models.fields.PrimaryKeyField import PrimaryKeyField
from core.models.GearModels import Gear
from core.models.MemberModels import Member
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

logger = logging.getLogger(__name__)


def validate_auth(authorizer):
    """Make sure that the person who authorized the transaction is in fact authorized to do so."""

    # If the member is not a staffer, then they are not allowed to authorize a transaction like this
    required_perm = "core.authorize_transactions"
    if not authorizer.has_permission(required_perm):
        msg = f"{authorizer.get_full_name()} is not allowed to authorize transactions"
        logger.info(msg)
        raise ValidationError(msg)


def validate_can_rent(member):
    """Ensure that the member is authorized to check out gear (is at least an active member)"""
    required_perm = "core.rent_gear"
    if not member.has_permission(required_perm):
        msg = (
            f"{member.get_full_name()} is not allowed to check out gear, "
            f"because they do not have the {required_perm} permission"
        )
        logger.info(msg)
        raise ValidationError(msg)


def validate_available(gear):
    """Ensure that the piece of gear is in fact available for checkout (is in stock)."""
    if not gear.is_available():
        msg = f"The {gear.name} with [{gear.rfid}] is not available for checkout because it is {gear.status}"
        logger.info(msg)
        raise ValidationError(msg)


def validate_rfid(rfid):
    """Ensure that the given rfid is unique across all tables containing rfids."""
    if rfid in get_all_rfids():
        msg = "This rfid is already in use!"
        logger.info(msg)
        raise ValidationError(msg)


def validate_required_certs(member, gear):
    """Validate that the member has all the certifications required to check out this piece of gear."""
    missing_certs = []
    for cert_required in gear.geartype.min_required_certs.all():
        if cert_required not in member.certifications.all():
            missing_certs.append(cert_required)
    if missing_certs:
        cert_names = [cert.title for cert in missing_certs]
        msg = f"{member.get_full_name()} is missing the following certifications: {cert_names}"
        logger.info(msg)
        raise ValidationError(msg)


class TransactionManager(models.Manager):
    """
    Manages Transactions, and ensures their effects are implemented.

    Every modification to any piece of gear should be done through a TransactionManager function, since transactions are
    intended to track any and all state changes of any piece of gear. The transaction creation functions also
    immediately implement the changes described by the transaction.
    """

    def __make_transaction(self, authorizer_rfid, type, gear, member=None, comments=""):
        """
        Make a transaction of any type in a safe and centralized way.

        :param authorizer_rfid: string, the rfid of the entity authorizing the transaction
        :param type: the type of the transaction
        :param gear: a gear model instance, the piece of gear that is being referred to
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
            comments=comments,
        )
        transaction.save(using=self._db)

        logger.info(
            f"{gear.name} was {type} by {member} authorized by {authorizer} {comments}"
        )

        return transaction

    def make_checkout(self, authorizer_rfid, gear_rfid, member_rfid, return_date):
        """
        Check out a piece of gear to a member and create a transaction logging the checkout.

        To check out a piece of gear, this function sets the status of that piece of gear to 1 ("Checked Out") and sets
        the ForeignKey on gear "checked_out_to" to the member that piece of gear is being checked out to. The comment
        is a note on when the gear is due back.

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
        validate_can_rent(member)
        validate_required_certs(member, gear)

        # If everything validated, we can try to make the transaction
        comment = f"Return date = {return_date.date}"
        transaction = self.__make_transaction(
            authorizer_rfid, "CheckOut", gear, member=member, comments=comment
        )

        # If the transaction was validated, then we can actually change the gear status
        gear.status = 1
        gear.checked_out_to = member
        gear.due_date = return_date
        gear.save()

        return transaction, gear

    def add_gear(
        self,
        authorizer_rfid,
        gear_rfid,
        geartype,
        gear_image,
        *required_certs,
        is_new=True,
        **init_data,
    ):
        """
        Create a new piece of gear and create a transaction logging the addition.

        Add a brand new piece of gear to the system, ensuring that the RFID is unique across all tables containing
        RFIDs. See GearModel for more information on the data supplied to Gear creation.

        :param authorizer_rfid: string, the 10-digit rfid of entity authorizing the transaction (should be staffer)\
        :param gear_rfid: string, the 10-digit rfid of the gear being added
        :param geartype: the type of gear that this is
        :param gear_image: AlreadyUploadedImage object with an image of this piece of gear
        :param required_certs: a list of the minimum certifications required to check this piece of gear out
        :param is_new: bool, notes whether this piece of gear was just acquired by the club. If the piece of gear is not
            newly acquired by the club, then it might be a piece of gear that lost it's tag!
        :param init_data: any additional data about the gear

        :return: Transaction (the transaction logging this gear addition), gear (the new piece of gear)
        """
        # First must make sure that the rfid is not in use by anything
        validate_rfid(gear_rfid)

        # Create the gear, because it is needed for creating the transaction
        gear = Gear.objects._create(gear_rfid, geartype, gear_image, **init_data)
        if required_certs:
            gear.min_required_certs.add(required_certs)
        gear.save()
        if is_new:
            comment = "Newly Acquired"
        else:
            comment = "Old Gear"

        # Make the transaction. This will also run all the necessary validations
        try:
            transaction = self.__make_transaction(
                authorizer_rfid, "Create", gear, comments=comment
            )
            logger.info("Gear was created")
        # If any validation failed, we need to undo the gear creation before aborting
        except ValidationError:
            gear.delete()
            msg = "This was not a valid gear creation. No gear was created"
            logger.info(msg)
            print(msg)
            raise

        # If everything went smoothly to this point, we can return the transaction logging the addition and the gear
        return transaction, gear

    def check_in_gear(self, authorizer_rfid, gear_rfid):
        """
        Check in a piece of gear and create a transaction logging the return.

        Change the status of a piece of gear to In Stock (available for rental), and remove the member it is checked out
        to. This should be called any time a previously checked out piece of gear becomes available for rental

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
        gear.due_date = None
        gear.save()

        return transaction, gear

    def retag_gear(self, authorizer_rfid, old_rfid, new_rfid):
        """
        Change the RFID of a piece of gear, and create a transaction logging the change.

        If for whatever reason a piece of gear loses it's RFID tag, then the RFID of that piece of gear must be changed
        in the system, but the rest of the properties of that piece of gear should not be changed.

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param old_rfid: string, the old 10-digit rfid of the piece of gear
        :param new_rfid: string, the new 10-digit rfid to give this piece of gear
        :return: ReTag Transaction
        """
        validate_rfid(new_rfid)
        gear = Gear.objects.get(rfid=old_rfid)

        # Create a transaction to ensure everything is authorized
        details = "Changed RFID from {} to {}".format(old_rfid, new_rfid)
        transaction = self.__make_transaction(
            authorizer_rfid, "ReTag", gear, comments=details
        )

        # If the transaction went through, we can go ahead and remove the gear
        gear.rfid = new_rfid
        gear.save()

        return transaction, gear

    def fix_gear(
        self, authorizer_rfid, gear_rfid, repairs_description, person_repairing
    ):
        """
        Note that a broken piece of gear was fixed and has been placed back in circulation

        If a piece of gear has been repaired sufficiently to be again usable, the repairs and the person doing the
        repairs should be noted, and the gear should be placed back in circulation

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :param repairs_description: a description of the repairs that were made
        :param person_repairing: the name of the person who preformed the repairs
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        comment = "{} {}".format(person_repairing, repairs_description)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(
            authorizer_rfid, "Fix", gear, comments=comment
        )

        gear.set_status = 0
        gear.save()
        return transaction, gear

    def break_gear(self, authorizer_rfid, gear_rfid, damage_description):
        """
        Note that a piece of gear is damaged and has been removed from circulation

        When a piece of gear is returned or otherwise found to be in a state such that it is too broken to be used, it
        should be noted as broken and removed from circulation until it is fixed. The STL should not be notified every
        time a piece of gear breaks, but should be notified every now and then.

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :param damage_description: a description of the damage and (if known) repairs needed
        :return: Break Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(
            authorizer_rfid, "Break", gear, comments=damage_description
        )

        gear.set_status = 2
        gear.save()

        return transaction, gear

    def missing_gear(self, authorizer_rfid, gear_rfid):
        """
        Note that a piece of gear has been missing for a while and should be searched for

        When a piece of gear has not been returned past it's due date, it is noted as missing. This gear will then be
        searched for via gear-calls or some other such method.

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)
        last_owner = gear.checked_out_to
        time_out = date.today()-gear.due_date
        details = f"Gear has been checked out for {time_out.days} days"

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(
            authorizer_rfid, "Missing", gear, member=last_owner, comments=details
        )

        gear.status = 3
        gear.save()
        return transaction, gear

    def expire_gear(self, authorizer_rfid, gear_rfid):
        """
        Note that a piece of gear has been missing for a very long time and is probably permanently lost

        When a piece of gear has been missing for a very long time, it becomes reasonable to assume that it will not be
        returned. This piece of gear should not be forgotten, but it should not be kept in the list of gear being
        actively searched for.

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear that got broken
        :return: Fix Transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)
        last_owner = gear.checked_out_to
        time_out = date.today()-gear.due_date
        details = f"Gear has been checked out for {time_out.days} days"

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(
            authorizer_rfid, "Dormant", gear, member=last_owner, comments=details
        )

        gear.status = 4
        gear.save()
        return transaction, gear

    def delete_gear(self, authorizer_rfid, gear_rfid, reason):
        """
        Permanently remove a piece of gear from circulation

        This should only be used when a piece of gear is being throw away. Since this is a dramatic action, the STL
        for the relevant department should get an email notifying them of the removal, in case it was not intentional

        :param authorizer_rfid: string, the 10-digit rfid of the entity authorizing the transaction
        :param gear_rfid: string, 10-digit rfid of the gear being deleted
        :param reason: string explaining why this piece of gear is being removed
        :return: transaction
        """
        gear = Gear.objects.get(rfid=gear_rfid)

        # Create a transaction to ensure everything is authorized
        transaction = self.__make_transaction(
            authorizer_rfid, "Delete", gear, comments=reason
        )

        # If the transaction went through, we can go ahead and remove the gear
        gear.status = 5
        gear.checked_out_to = None
        gear.department.notify_gear_removed()

        return transaction, gear

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

        member = Member.objects.get(rfid=authorizer_rfid)
        if not member.has_permission("core.change_gear"):
            raise ValidationError("You don't have the permission to change gear!")

        # All the changes made will be described here
        action = f"Admin override on {gear} [{gear_rfid}]: \n"

        # Remove the fields that were appended from the geartype, they will be saved in gear_data
        for field_name in gear.geartype.get_field_names():
            kwargs.pop(field_name)

        # Set each of the available kwargs to their desired value if they are not none
        for kwarg in kwargs.keys():

            new_value = kwargs[kwarg]
            old_value = gear.__getattribute__(kwarg)

            if new_value != old_value:
                gear.__setattr__(kwarg, new_value)

                # Parse gear data action differently to not spew a bunch of unnecessary internal data
                if kwarg == "gear_data":
                    old_gear_data = json.loads(old_value)
                    new_gear_data = json.loads(new_value)
                    for field_name in new_gear_data.keys():
                        # Save the action as a change for each data field individually
                        old_field_value = old_gear_data[field_name]["initial"]
                        new_field_value = new_gear_data[field_name]["initial"]
                        if old_field_value != new_field_value:
                            action += f"  Changed {field_name} from {old_field_value} to {new_field_value}"

                else:
                    action += f"  Changed {kwarg} from {old_value} to {new_value};"

        # Save the changes made in a transaction
        transaction = self.__make_transaction(
            authorizer_rfid, "Override", gear, comments=action
        )
        return transaction, gear


class Transaction(models.Model):
    """
    Model that stores the data for every transaction, to allow better monitoring of the status of the whole system.

    Each change to any piece of gear should be done via a transaction manager function. This allows transactions to
    serve as state change vectors for the system, and the status of the system at any time could be reconstructed from
    the addition (subsequent application) of these transactions.

    NEVER CREATE TRANSACTIONS MANUALLY, ALWAYS USE THE MANAGER FUNCTIONS
    """

    objects = TransactionManager()

    transaction_types = [
        (
            "Rental",
            (
                ("CheckOut", "Check Out"),
                ("CheckIn", "Check In"),
                ("Inventory", "In Stock"),
            ),
        ),
        (
            "Admin Actions",
            (
                ("Create", "New Gear"),
                ("Delete", "Remove Gear"),
                ("ReTag", "Change Tag"),
                ("Break", "Set Broken"),
                ("Fix", "Set Fixed"),
                ("Override", "Admin Change"),
            ),
        ),
        ("Auto Updates", (("Missing", "Gear Missing"), ("Expire", "Gear Expiration"))),
    ]

    primary_key = PrimaryKeyField()

    #: The time at which this transaction was created - will be automatically set and cannot be changed
    timestamp = models.DateTimeField(auto_now_add=True)

    #: A string defining the type of transaction this is (see transaction types)
    type = models.CharField(max_length=20, choices=transaction_types)

    #: The piece of gear this transaction relates to: MUST EXIST
    gear = models.ForeignKey(
        Gear,
        null=False,
        on_delete=models.PROTECT,
        related_name="has_checked_out",
        validators=[validate_available],
    )

    #: If this transaction relates to a member, that member should be referenced here
    member = models.ForeignKey(Member, null=True, on_delete=models.PROTECT)

    #: Either SYSTEM or a String of the rfid of the person who authorized the transaction
    authorizer = models.ForeignKey(
        Member,
        null=False,
        on_delete=models.PROTECT,
        related_name="has_authorized",
        validators=[validate_auth],
    )

    #: Any additional notes to be saved about this transaction
    comments = models.TextField(default="")

    def __str__(self):
        return "{} Transaction for a {}".format(self.type, self.gear.name)

    @property
    def detail_url(self):
        return reverse("admin:core_transaction_detail", kwargs={"pk": self.pk})
