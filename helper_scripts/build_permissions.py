from helper_scripts import setup_django

from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.GearModels import CustomDataField, Gear, GearType
from core.models.MemberModels import Member, Staffer
from core.models.QuizModels import Answer, Question
from core.models.TransactionModels import Transaction
from core.models.FileModels import AlreadyUploadedImage
from api.models import MemberRFIDCheck
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction

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
gear_type_type = ContentType.objects.get_for_model(GearType)
custom_field_type = ContentType.objects.get_for_model(CustomDataField)
group_type = ContentType.objects.get_for_model(Group)
question_type = ContentType.objects.get_for_model(Question)
answer_type = ContentType.objects.get_for_model(Answer)
image_type = ContentType.objects.get_for_model(AlreadyUploadedImage)
rfid_check_type = ContentType.objects.get_for_model(MemberRFIDCheck)


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
    add_permission(
        codename="view_staffer",
        name="Can see staffer information",
        content_type=staffer_type,
    )
    add_permission(
        codename="check_availability_gear",
        name="Check to see if the club has gear available",
        content_type=gear_type,
    )
    add_group("Just Joined", all_permissions)


def build_expired():
    """Create permissions for expired members"""
    add_group("Expired", all_permissions)


def build_member():
    """Create permissions for regular, active members"""
    add_permission(
        codename="is_active_member",
        name="Is an active member",
        content_type=member_type,
    )
    add_permission(
        codename="rent_gear", name="Allowed to rent gear", content_type=gear_type
    )
    add_permission(
        codename="view_gear",
        name="Has access to at least one item on the gear list",
        content_type=gear_type,
    )
    add_permission(
        codename="view_department",
        name="Can see department information",
        content_type=department_type,
    )
    add_permission(
        codename="view_certification",
        name="Can see certification information",
        content_type=certification_type,
    )
    add_permission(
        codename="view_transaction",
        name="Can view transactions",
        content_type=transaction_type,
    )
    add_group("Member", all_permissions)


def build_staffer():
    """Create permissions for regular staffers"""
    add_permission(
        codename="add_gear", name="Can add a piece of gear", content_type=gear_type
    )
    add_permission(
        codename="change_gear",
        name="Can change the info on gear",
        content_type=gear_type,
    )
    add_permission(
        codename="view_general_gear",
        name="Can see and search the gear list",
        content_type=gear_type,
    )
    add_permission(
        codename="authorize_transactions",
        name="Can authorize transactions",
        content_type=transaction_type,
    )
    add_permission(
        codename="view_member",
        name="Can view all member info",
        content_type=member_type,
    )
    add_permission(
        codename="view_all_members",
        name="Can view all member info",
        content_type=member_type,
    )
    add_permission(
        codename="view_all_transactions",
        name="Can see all the gear transactions ever created",
        content_type=transaction_type,
    )
    add_permission(
        codename="add_member", name="Can add new members", content_type=member_type
    )
    add_permission(
        codename="change_member",
        name="Can do arbitrary changes to members",
        content_type=member_type,
    )
    add_permission(
        codename="view_gear_type",
        name="Can view gear types",
        content_type=gear_type_type,
    )
    add_permission(
        codename="add_alreadyuploadedimage",
        name="Can add and Already Uploaded Image",
        content_type=image_type,
    )
    add_permission(
        codename="view_memberrfidcheck",
        name="View member RFID check log",
        content_type=rfid_check_type,
    )
    add_group("Staff", all_permissions)


def build_board():
    """Create a group of the board members who have extra permissions on a club-wide scale"""
    add_permission(
        codename="view_all_gear",
        name="Can view gear with any status",
        content_type=gear_type,
    )
    add_permission(
        codename="remove_gear",
        name="Can set gear to removed status",
        content_type=gear_type,
    )
    add_permission(
        codename="add_gear_type",
        name="Can change gear types",
        content_type=gear_type_type,
    )
    add_permission(
        codename="delete_gear_type",
        name="Can delete gear types",
        content_type=gear_type_type,
    )
    add_permission(
        codename="add_customdatafield",
        name="Can add custom data fields",
        content_type=custom_field_type,
    )
    add_permission(
        codename="change_customdatafield",
        name="Can change custom data fields",
        content_type=custom_field_type,
    )
    add_permission(
        codename="delete_customdatafield",
        name="Can delete custom data fields",
        content_type=custom_field_type,
    )
    add_permission(
        codename="add_staffer",
        name="Can promote members to staffers",
        content_type=staffer_type,
    )
    add_permission(
        codename="change_staffer",
        name="Can change staffer data",
        content_type=staffer_type,
    )
    add_permission(
        codename="add_department",
        name="Can add departments to the club",
        content_type=department_type,
    )
    add_permission(
        codename="change_department",
        name="Can change departments at the club",
        content_type=department_type,
    )
    add_permission(
        codename="delete_department",
        name="Can delete departments from the club",
        content_type=department_type,
    )
    add_permission(
        codename="add_certification",
        name="Can add gear checkout certifications",
        content_type=certification_type,
    )
    add_permission(
        codename="change_certification",
        name="Can change gear checkout certifications",
        content_type=certification_type,
    )
    add_permission(
        codename="delete_certification",
        name="Can delete gear checkout certifications",
        content_type=certification_type,
    )
    add_group("Board", all_permissions)


def build_admin():
    """Create the admin group, which has all possible permissions"""
    add_permission(
        codename="add_group", name="Can add permission groups", content_type=group_type
    )
    add_permission(
        codename="change_group",
        name="Can change permission groups",
        content_type=group_type,
    )
    add_permission(
        codename="delete_group",
        name="Can delete permission groups",
        content_type=group_type,
    )
    add_permission(
        codename="delete_gear",
        name="Can permanently delete gear from the database (DANGER)",
        content_type=gear_type,
    )
    add_permission(
        codename="delete_staffer", name="Can delete staffers", content_type=staffer_type
    )
    add_permission(
        codename="add_question",
        name="Can add quiz questions",
        content_type=question_type,
    )
    add_permission(
        codename="change_question",
        name="Can change quiz questions",
        content_type=question_type,
    )
    add_permission(
        codename="delete_question",
        name="Can delete quiz questions",
        content_type=question_type,
    )
    add_permission(
        codename="add_answer", name="Can add quiz answers", content_type=answer_type
    )
    add_permission(
        codename="change_answer",
        name="Can change quiz answers",
        content_type=answer_type,
    )
    add_permission(
        codename="delete_answer",
        name="Can delete quiz answers",
        content_type=answer_type,
    )
    add_permission(
        codename="delete_alreadyuploadedimage",
        name="Can delete and Already Uploaded Image",
        content_type=image_type,
    )
    add_permission(
        codename="change_alreadyuploadedimage",
        name="Can change and Already Uploaded Image",
        content_type=image_type,
    )
    add_permission(
        codename="delete_member",
        name="Can delete existing members",
        content_type=member_type,
    )
    add_group("Admin", all_permissions)


def add_group(name, permissions):
    """Add the group, only creating it if it doesn't already exist"""
    try:
        with transaction.atomic():
            group = Group.objects.create(name=name)
    except IntegrityError:
        group = Group.objects.get(name=name)

    group.permissions.set(permissions)
    group.save()
    return group


def add_permission(codename=None, name=None, content_type=None):
    """Add the permission, only creating if it does not already exist"""
    try:
        with transaction.atomic():  # Resolves a quirk with how django handles the test database
            permission = Permission.objects.create(
                codename=codename, name=name, content_type=content_type
            )
    except IntegrityError:
        permission = Permission.objects.get(codename=codename)

    all_permissions.append(permission)
    return permission


if __name__ == "__main__":
    build_all()
