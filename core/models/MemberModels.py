import os

from django.db import models
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta, datetime
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, Group

from phonenumber_field.modelfields import PhoneNumberField

from .CertificationModels import Certification
from .fields.RFIDField import RFIDField


class MemberManager(BaseUserManager):
    def create_member(self, email, rfid, membership_duration, password=None):
        """
        Creates and saves a Member with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # Trying to add the max timedelta to now results in an overflow, so handle the superuser case separately
        try:
            expiration_date = now() + membership_duration
        except OverflowError:
            expiration_date = datetime.max

        member = self.model(
            email=self.normalize_email(email),
            rfid=rfid,
            date_expires=expiration_date
        )
        member.set_password(password)
        member.save(using=self._db)

        member.groups.set([Group.objects.get(name="Just Joined")])
        member.save(using=self._db)

        return member

    def create_superuser(self, email, rfid, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        superuser = self.create_member(
            email=email,
            rfid=rfid,
            membership_duration=timedelta.max,
            password=password,
        )

        # Add the rest of the data about the superuser
        superuser.is_admin = True
        superuser.first_name = "Master"
        superuser.last_name = "Admin"
        superuser.phone_number = '+15555555555'
        superuser.certifications.set(Certification.objects.all())
        superuser.save(using=self._db)

        superuser.groups.set([Group.objects.get(name="Admin")])
        superuser.save(using=self._db)
        return superuser


class StafferManager(models.Manager):
    def upgrade_to_staffer(self, member, staffname, autobiography=None):
        """
        Begins the process of turning a member into a staffer

        :param member: the member to make a staffer
        :param staffname: the prefix (before @) part of the staffer's staff email
        :return: Staffer
        """
        exc_email = "{}@excursionclubucsb.org".format(staffname)
        member.groups.set([Group.objects.get(name="Staff")])
        member.date_expires = datetime.max
        member.save()
        if autobiography is not None:
            staffer = self.model(member=member, exc_email=exc_email, autobiography=autobiography)
        else:
            staffer = self.model(member=member, exc_email=exc_email)
        staffer.save()
        return staffer


class Member(AbstractBaseUser):
    """This is the base model for all members (this includes staffers)"""
    objects = MemberManager()

    groups = models.ManyToManyField(to=Group)

    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    rfid = RFIDField(verbose_name="RFID")
    picture = models.ImageField(
        verbose_name="Profile Picture",
        upload_to="ProfilePics/",
        null=True
    )
    phone_number = PhoneNumberField(unique=True, null=True)

    date_joined = models.DateField(auto_now_add=True)
    date_expires = models.DateField(null=False)

    is_admin = models.BooleanField(default=False)
    certifications = models.ManyToManyField(Certification)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rfid', 'date_expires']

    @property
    def is_staff(self):
        """
        Property that is used by django to determine whether a user is allowed to log in to the admin
        """
        just_joined = self.groups.filter(name='Just Joined')
        expired = self.groups.filter(name='Expired')
        return not (just_joined or expired)

    @property
    def is_staffer(self):
        """Returns true if this member has staffer privileges"""
        staffer_group = self.groups.filter(name='Staff')
        board_group = self.groups.filter(name='Board')
        admin_group = self.groups.filter(name='Admin')
        return staffer_group or board_group or admin_group

    def has_name(self):
        """Check whether the name of this member has been set"""
        return self.first_name and self.last_name

    def get_full_name(self):
        """Return the full name if it is know, or 'New Member' if it is not"""
        if self.has_name():
            return "{first} {last}".format(first=self.first_name, last=self.last_name)
        else:
            return "New Member"
    get_full_name.short_description = "Full Name"

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):
        """
        If we know the name of the user, then display their name, otherwise use their email
        """
        if self.has_name():
            return self.get_full_name()
        else:
            return self.email

    def get_group(self):
        """Get's a string representing this members group membership"""
        group_name = ""
        for group in self.groups.all():
            group_name += group.name + " "
        return group_name

    def update_admin(self):
        """Updates the admin status of the user in the django system"""
        if self.groups.get(name="Admin"):
            self.is_admin = True
        else:
            self.is_admin = False

    def expire(self):
        """Expires this member's membership"""
        self.groups.set(Group.objects.get(name="Expired"))

    def send_email(self, title, body, from_email='system@excursionclubucsb.org'):
        """Sends an email to the member"""
        send_mail(title, body, from_email, [self.email], fail_silently=False)

    def send_intro_email(self, finish_signup_url):
        """Send the introduction email with the link to finish signing up to the member"""
        title = "Finish Signing Up"
        # get the absolute path equivalent of going up one level and then into the templates directory
        templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'templates'))
        template_file = open(os.path.join(templates_dir, 'emails', 'intro_email.txt'))
        template = template_file.read()
        body = template.format(finish_signup_url=finish_signup_url)
        self.send_email(title, body, from_email='membership@excursionclubucsb.org')

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True


class Staffer(models.Model):
    """This model provides the staffer profile (all the extra data that needs to be known about staffers)"""
    objects = StafferManager()

    def __str__(self):
        """Gives the staffer a string representation of the staffer name"""
        return self.member.get_full_name()

    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    exc_email = models.EmailField(
        verbose_name='Official ExC Email',
        max_length=255,
        unique=True,
    )
    autobiography = models.TextField(verbose_name="Self Description of the staffer",
                                     default="I am too lazy and lame to upload a bio!")
