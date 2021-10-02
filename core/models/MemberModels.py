from core.models.fields.PrimaryKeyField import PrimaryKeyField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime, now, timedelta
from uwccsystem import settings
from phonenumber_field.modelfields import PhoneNumberField
from core.convinience import get_email_template

from .CertificationModels import Certification
from .fields.RFIDField import RFIDField
from core import emailing


def get_profile_pic_upload_location(instance, filename):
    """Save profile pictures in object store"""
    extension = filename.split(".")[-1]

    # Get the name with all special characters removed
    name_str = "".join(e for e in instance.get_full_name() if e.isalnum())
    year = datetime.now().year

    # Assemble file location and insert date data
    location = f"ProfilePics/{year}/{name_str}.{extension}"
    location = datetime.strftime(datetime.now(), location)
    return location


class MemberManager(BaseUserManager):
    def create_member(self, email, rfid, membership_duration, password=None):
        """
        Creates and saves a Member with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        # Trying to add the max timedelta to now results in an overflow, so handle the superuser case separately
        try:
            expiration_date = now() + membership_duration
        except OverflowError:
            expiration_date = datetime.max

        member = self.model(
            email=self.normalize_email(email), rfid=rfid, date_expires=expiration_date
        )
        member.set_password(password)
        member.save(using=self._db)

        member.move_to_group("Just Joined")

        return member

    def create_superuser(self, email, rfid, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        superuser = self.create_member(
            email=email, rfid=rfid, membership_duration=timedelta.max, password=password
        )

        # Add the rest of the data about the superuser
        superuser.is_admin = True
        superuser.first_name = "Master"
        superuser.last_name = "Admin"
        superuser.phone_number = "808-555-0125"
        superuser.certifications.set(Certification.objects.all())
        superuser.save(using=self._db)

        superuser.move_to_group("Admin")

        return superuser


class StafferManager(models.Manager):
    def upgrade_to_staffer(self, member, staff_name, autobiography=None):
        """
        Begins the process of turning a member into a staffer

        :param member: the member to make a staffer
        :param staff_name: the prefix (before @) part of the staffer's staff email
        :param autobiography: the staffers life story
        :return: Staffer
        """
        exc_email = f"{staff_name}{settings.CLUB_EMAIL}"
        member.move_to_group("Staff")
        member.date_expires = datetime.max
        member.save()

        staffer = self.model(member=member, exc_email=exc_email, nickname=staff_name)
        staffer.is_active = True
        if autobiography:
            staffer.autobiography = None
        staffer.save()

        member.send_new_staff_email(staffer)
        return staffer


class Member(AbstractBaseUser, PermissionsMixin):
    """This is the base model for all members (this includes staffers)"""

    objects = MemberManager()
    primary_key = PrimaryKeyField()

    # Personal contact information
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    image = models.ImageField(
        verbose_name="Profile Picture",
        default=settings.DEFAULT_IMG,
        upload_to=get_profile_pic_upload_location,
        blank=True,
        null=True,
    )
    phone_number = PhoneNumberField(unique=False, null=True)

    # Emergency contact information
    emergency_contact_name = models.CharField(max_length=100, verbose_name="Contact Name", null=True)
    emergency_relation = models.CharField(max_length=50, verbose_name="Relationship", null=True)
    emergency_phone = PhoneNumberField(unique=False, verbose_name="Phone Number", null=True)
    emergency_email = models.EmailField(unique=False, verbose_name="Best Email", null=True)

    # Membership data
    date_joined = models.DateField(auto_now_add=True)
    date_expires = models.DateField(null=False)
    rfid = RFIDField(verbose_name="RFID")
    group = models.CharField(default="Unset", max_length=30)
    is_admin = models.BooleanField(default=False)
    certifications = models.ManyToManyField(Certification, blank=True)

    #: This is used by django to determine if users are allowed to login. Leave it, except when banishing someone
    is_active = models.BooleanField(
        default=True
    )  # Use is_active_member to check actual activity

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["date_expires"]

    @property
    def is_active_member(self):
        """Return true if the member has a valid membership"""
        return self.has_permission("core.is_active_member")

    @property
    def is_staff(self):
        """
        Property that is used by django to determine whether a user is allowed to log in to the admin: i.e. everyone
        """
        return True

    @property
    def is_staffer(self):
        """Property to check if a member is a excursion staffer or not"""
        return self.group in ['Staff', 'Board', 'Admin']

    @property
    def edit_profile_url(self):
        return reverse("admin:core_member_change", kwargs={"object_id": self.pk})

    @property
    def view_profile_url(self):
        return reverse("admin:core_member_detail", kwargs={"pk": self.pk})

    @property
    def make_staff_url(self):
        return reverse('admin:core_staffer_add', kwargs={'member': self})

    def has_name(self):
        """Check whether the name of this member has been set"""
        return self.first_name and self.last_name

    def get_full_name(self):
        """Return the full name if it is know, or 'New Member' if it is not"""
        if self.has_name():
            return f"{self.first_name} {self.last_name}"
        else:
            return "New Member"

    get_full_name.short_description = "Full Name"

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def get_all_certifications(self):
        all_certs = self.certifications.all()
        return all_certs

    def has_no_certifications(self):
        return len(self.certifications.all()) == 0

    def __str__(self):
        """
        If we know the name of the user, then display their name, otherwise use their email
        """
        if self.has_name():
            return self.get_full_name()
        else:
            return self.email

    def update_admin(self):
        """Updates the admin status of the user in the django system"""
        self.is_admin = self.groups.name == "Admin"

    def expire(self):
        """Expires this member's membership"""
        self.move_to_group("Expired")

    def promote_to_active(self):
        """Move the member to the group of active members"""
        if self.group == "Staff" or self.group == "Board" or self.group == "Admin":
            print("Member status is already better than member")
        else:
            self.move_to_group("Member")

    def extend_membership(self, duration, rfid="", password=""):
        """Add the given amount of time to this member's membership, and optionally update their rfid and password"""

        self.move_to_group("Just Joined")

        if self.date_expires < datetime.date(now()):
            self.date_expires = now() + duration
        else:
            self.date_expires += duration

        if rfid:
            self.rfid = rfid

        if password:
            self.set_password(password)

        return self

    def send_email(self, title, body, from_email):
        """Sends an email to the member"""
        emailing.send_email(
            [self.email],
            title,
            body,
            from_email=from_email,
            from_name='Excursion Club',
            receiver_names=[self.get_full_name()]
        )

    def send_membership_email(self, title, body):
        """Send an email to the member from the membership email"""
        emailing.send_membership_email(
            [self.email],
            title,
            body,
            receiver_names=[self.get_full_name()]
        )

    def send_intro_email(self, finish_signup_url):
        """Send the introduction email with the link to finish signing up to the member"""
        title = "Finish Signing Up"
        template = get_email_template('intro_email')
        body = template.format(finish_signup_url=finish_signup_url)
        self.send_membership_email(title, body)

    def send_expires_soon_email(self):
        """Send an email warning the member that their membership will soon expire"""
        title = "Climbing Club Membership Expiring Soon!"
        template = get_email_template('expire_soon_email')
        body = template.format(member_name=self.get_full_name(), expiration_date=self.date_expires)
        self.send_membership_email(title, body)

    def send_expired_email(self):
        """Send an email warning the member that their membership will soon expire"""
        title = "Climbing Club Membership Expired!"
        template = get_email_template('expired_email')
        body = template.format(member_name=self.get_full_name(), today=self.date_expires)
        self.send_membership_email(title, body)

    def send_missing_gear_email(self, all_gear):
        """Send an email to member that they have gear to return"""
        gear_rows = []
        for gear in all_gear:
            gear_rows.append(f"<tr><td>{gear.name}</td><td>{gear.due_date.strftime('%a, %b %d, %Y')}</td></tr>")
        template = get_email_template('missing_gear')
        body = template.format(first_name=self.first_name, gear_rows="".join(gear_rows))
        title = 'Gear Overdue'
        self.send_email(
            title,
            body,
            'info@climbingclubuw.org',
        )

    def send_new_staff_email(self, staffer):
        """Sen an email welcoming the member to staff"""
        title = "Welcome to staff!"
        template = get_email_template('new_staffer')
        body = template.format(
            member_name=self.first_name,
            finish_url=settings.WEB_BASE+staffer.edit_profile_url,
            staffer_email=staffer.exc_email
        )
        self.send_membership_email(title, body)

    def has_module_perms(self, app_label):
        """This is required by django, determine whether the user is allowed to view the app"""
        return True

    def has_permission(self, permission_name):
        """Loop through all the permissions of the group associated with this member to see if they have this one"""
        return self.has_perm(permission_name)

    def move_to_group(self, group_name):
        """
        Convenience function to move a member to a group

        Always use this function since it changes the group and the group shortcut field
        """
        new_group = Group.objects.filter(name=group_name)
        self.groups.set(new_group)
        self.group = str(new_group[0])
        self.save()


class Staffer(models.Model):
    """This model provides the staffer profile (all the extra data that needs to be known about staffers)"""

    objects = StafferManager()

    member = models.OneToOneField(Member, on_delete=models.CASCADE)

    is_active = models.BooleanField(
        default=False, null=True)
    nickname = models.CharField(
        max_length=40,
        blank=True,
        null=True)
    favorite_trips = models.TextField(
        blank=True,
        null=True,
        help_text="List of your favorite trips, one per line")
    exc_email = models.EmailField(
        verbose_name='Official Club Email',
        max_length=255,
        unique=True)
    title = models.CharField(
        verbose_name="Position Title",
        default="Climbing Club Staff!",
        max_length=30)
    autobiography = models.TextField(
        verbose_name="Self Description of the staffer",
        default="I am too lazy and lame to upload a bio!",
        null=True)

    @property
    def full_name(self):
        """Gets the name of the member associated with this staffer"""
        return self.member.get_full_name()

    def __str__(self):
        """Gives the staffer a string representation of the staffer name"""
        return str(self.member)

    @property
    def fav_trip_list(self):
        if self.favorite_trips:
            trips = self.favorite_trips.split("\n")
        else:
            trips = ["I'm stoked on all types of things!", ]
        return trips

    @property
    def edit_profile_url(self):
        return reverse("admin:core_staffer_change", kwargs={"object_id": self.pk})
