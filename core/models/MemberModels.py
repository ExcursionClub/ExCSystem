from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from phonenumber_field.modelfields import PhoneNumberField


class MemberManager(BaseUserManager):
    def create_member(self, email, rfid, first_name, last_name, phone_number, password=None):
        """
        Creates and saves a Member with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        member = self.model(
            email=self.normalize_email(email),
            rfid=rfid,
            first_name=first_name,
            last_name=last_name,
            date_joined=now(),
            phone_number=phone_number
        )

        member.set_password(password)
        member.save(using=self._db)

        return member

    def create_superuser(self, email, rfid, first_name, last_name, phone_number, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        superuser = self.create_member(
            email=email,
            rfid=rfid,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password
        )
        superuser.is_admin = True
        superuser.status = 7
        superuser.save(using=self._db)
        return superuser


class Member(AbstractBaseUser):
    """This is the base model for all members (this includes staffers)"""

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    rfid = models.CharField(
        verbose_name="RFID",
        max_length=10,
        unique="True"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    picture = models.ImageField(verbose_name="Profile Picture", upload_to="ProfilePics/")
    phone_number = PhoneNumberField(unique=True)
    date_joined = models.DateField(default=now())
    is_admin = models.BooleanField(default=False)

    status_choices = [
        ('Member', [
                (0, "Just Joined"),
                (1, "Expired Member"),
                (2, "Active Member"),
            ],
        ),
        ('Staffer', [
                (3, "Prospective Staffer"),
                (4, "Expired Staffer"),
                (5, "Active Staffer"),
                (6, "Board Member"),
                (7, "Admin")
            ],
        ),
    ]
    status = models.IntegerField(default=0, choices=status_choices)

    objects = MemberManager()

    print(picture.storage.url)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rfid', 'first_name', 'last_name', 'phone_number']

    def get_full_name(self):
        # The user is identified by their email address
        return "{} {}".format(self.first_name, self.last_name)
    get_full_name.short_description = "Full Name"

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def update_admin(self):
        """Updates the admin status of the user in the django system"""
        if self.status == 7:
            self.is_admin = True
        else:
            self.is_admin = False

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """
        Property that allows and easy check for whether the member is a staffer
        """
        # If the member is a prospective staffer or better, then they are given staff privileges
        if self.status >= 4:
            return True
        else:
            return False


class Staffer(models.Model):
    """This model provides the staffer profile (all the extra data that needs to be known about staffers)"""
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    exc_email = models.EmailField(
        verbose_name='Official ExC Email',
        max_length=255,
        unique=True,
    )
    autobiography = models.TextField(verbose_name="Self Description of the staffer")
