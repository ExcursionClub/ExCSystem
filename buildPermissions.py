from django.db import IntegrityError, transaction
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.MemberModels import Member, Staffer
from core.models.GearModels import Gear
from core.models.TransactionModels import Transaction


"""
As permissions are created, they are appended here. Then, all these permissions are appended to the next group. That
way, every group also contains the permissions of all the lower groups
"""
all_permissions = []

certification_type = ContentType.objects.get_for_model(Certification)
department_type = ContentType.objects.get_for_model(Department)
member_type = ContentType.objects.get_for_model(Member)
staffer_type = ContentType.objects.get_for_model(Staffer)
transaction_type = ContentType.objects.get_for_model(Transaction)
gear_type = ContentType.objects.get_for_model(Gear)


def build_all():
    """Build all the groups. Must be done in ascending order of power"""
    build_just_joined()
    build_expired()
    build_member()
    build_staffer()
    build_board()
    build_admin()


def build_just_joined():
    """Create all the permissions for the lowest group, of freshly joined members"""
    just_joined = Group.objects.create(name="Just Joined")
    add_permission(
        codename="view_staffer",
        name="Can see staffer information",
        content_type=staffer_type)
    add_permission(
        codename="check_availability_gear",
        name="Check to see if the club has gear available",
        content_type=gear_type)
    just_joined.permissions.set(all_permissions)
    just_joined.save()


def build_expired():
    """Create permissions for expired members"""
    expired = Group.objects.create(name="Expired")
    expired.permissions.set(all_permissions)
    expired.save()


def build_member():
    """Create permissions for regular, active members"""
    member = Group.objects.create(name="Member")
    add_permission(
        codename="rent_gear",
        name="Allowed to rent gear",
        content_type=gear_type)
    add_permission(
        codename="view_gear",
        name="Can see and search the gear list",
        content_type=gear_type)
    member.permissions.set(all_permissions)
    member.save()


def build_staffer():
    """Create permissions for regular staffers"""
    staffer = Group.objects.create(name="Staff")
    add_permission(
        codename="add_gear",
        name="Can add a piece of gear",
        content_type=gear_type)
    add_permission(
        codename="change_gear",
        name="Can change the info on gear",
        content_type=gear_type)
    add_permission(
        codename="checkout_gear",
        name="Can check gear out to somone else",
        content_type=gear_type)
    add_permission(
        codename="checkin_gear",
        name="Can check returned gear back in",
        content_type=gear_type)
    add_permission(
        codename="view_member",
        name="Can view all member info",
        content_type=member_type)
    add_permission(
        codename="view_all_transactions",
        name="Can see all the gear transactions ever created",
        content_type=transaction_type)
    add_permission(
        codename="add_member",
        name="Can add new members",
        content_type=member_type)
    add_permission(
        codename="change_info_member",
        name="Can change member personal information",
        content_type=member_type)
    add_permission(
        codename="change_membership",
        name="Can change member membership",
        content_type=member_type)
    staffer.permissions.set(all_permissions)
    staffer.save()


def build_board():
    """Create a group of the board members who have extra permissions on a club-wide scale"""
    board = Group.objects.create(name="Board")
    add_permission(
        codename="view_all_gear",
        name="Can view gear with any status",
        content_type=gear_type)
    add_permission(
        codename="add_staffer",
        name="Can promote members to staffers",
        content_type=staffer_type)
    add_permission(
        codename="add_department",
        name="Can add departments to the club",
        content_type=department_type)
    add_permission(
        codename="change_member",
        name="Can do arbitrary changes to change member",
        content_type=member_type)
    board.permissions.set(all_permissions)
    board.save()


def build_admin():
    """Create the admin group, which has all possible permissions"""
    admin = Group.objects.create(name="Admin")
    admin.permissions.set(Permission.objects.all())
    admin.save()
    
    
def add_permission(codename=None, name=None, content_type=None):
    """Add the permission, only creating if it does not already exist"""
    try:
        with transaction.atomic():  # Resolves a quirk with how django handles the test database
            permission = Permission.objects.create(codename=codename, name=name, content_type=content_type)
    except IntegrityError:
        permission = Permission.objects.get(codename=codename)
    
    all_permissions.append(permission)
    return permission

