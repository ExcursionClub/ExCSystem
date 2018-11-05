"""Populate the database with a complete set of randomly generated data"""

import os
from random import choice, randint
from typing import Any, List, Optional

import setupDjango

import kiosk.CheckoutLogic as logic
import names
import progressbar
from core.models.DepartmentModels import Department
from core.models.MemberModels import Member, Staffer
from core.models.TransactionModels import Transaction
from core.models.GearModels import GearType, CustomDataField
from core.models.FileModels import AlreadyUploadedImage
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.timezone import timedelta

import buildBasicData
buildBasicData.build_all()

ADMIN_RFID = '0000000000'
SYSTEM_RFID = '1111111111'
PASSWORD = 'admin'

used_rfids = [ADMIN_RFID, SYSTEM_RFID]
used_phones: List[Optional[str]] = []

RFIDS_TO_HAND_OUT = [
    '1000000000', '2000000000', '3000000000', '4000000000', '5000000000', '6000000000', '7000000000'
]


def gen_rfid() -> str:
    """generates a random and unique rfid"""
    rfid = str(randint(1000000000, 9999999999))
    if rfid in used_rfids:
        rfid = gen_rfid()
    else:
        used_rfids.append(rfid)
    return rfid


def gen_phone_num() -> str:
    """Generates a random and unique phone number"""
    phone = '+{}{}'.format(randint(1, 45), randint(1000000000, 9999999999))
    if phone in used_phones:
        phone = gen_phone_num()
    else:
        used_phones.append(phone)
    return phone


def gen_duration() -> List[timedelta]:
    """Randomly pick a duration of either 90 or 365 days"""
    durations = [timedelta(days=90), timedelta(days=365)]
    return choice(durations)


def pick_random(element_list: List[Any]) -> Any:
    """Picks and returns a random element from the provided list"""
    return choice(element_list)


def generate_rand_member() -> Member:
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    membership_duration = gen_duration()
    email = "{}.{}@fakeemail.lol".format(first_name, last_name)
    rfid = gen_rfid()

    try:
        random_member = Member.objects.create_member(
            email, rfid, membership_duration=membership_duration, password=PASSWORD
        )
        random_member.first_name = first_name
        random_member.last_name = last_name
        random_member.phone_number = gen_phone_num()
        random_member.save()
    # If anything goes wrong when making this member, try again
    except IntegrityError:
        random_member = generate_rand_member()

    return random_member


# Add the master admin  and excursion system accounts
admin = Member.objects.create_superuser(
    "admin@excursionclubucsb.org", ADMIN_RFID, password=PASSWORD
)
system = Member.objects.create_member(
    "system@excursionclubucsb.org", SYSTEM_RFID, membership_duration=timedelta.max,
    password=PASSWORD
)
Staffer.objects.upgrade_to_staffer(
    system, "ExCSystem",
    "I am the Excursion computer system, and I do all the work nobody else can or wants to do"
)

# Add dummy members
print('Making members...')
total_number_members = 100
number_new = int(total_number_members / 5)
number_expired = int(total_number_members / 3)
member_rfids = []
bar = progressbar.ProgressBar()
for i in bar(range(total_number_members)):

    member = generate_rand_member()
    member_rfids.append(member.rfid)
    # Members are made to be new by default
    # After the correct number of new members are made, start making expired members
    if number_new < i < (number_new + number_expired):
        member.group = Group.objects.get(name="Expired")
        member.save()
    # The rest of the members should be active
    elif i > (number_new + number_expired):
        member.group = Group.objects.get(name="Member")
        member.save()
print('')
print('Made members')

# Add some staffers
print('Making staffers...')
number_staffers = 10
staffer_rfids = []
bar = progressbar.ProgressBar()
for i in bar(range(number_staffers)):
    member = generate_rand_member()
    member_rfids.append(member.rfid)
    staffer_rfids.append(member.rfid)
    nickname = member.first_name + str(i)
    member.save()
    staffer = Staffer.objects.upgrade_to_staffer(member, nickname)
    staffer.save()

# Add staffer with known rfid
member = generate_rand_member()
member.rfid = 1234567890
member_rfids.append(member.rfid)
staffer_rfids.append(member.rfid)
nickname = member.first_name + "RFIDKnown"
member.save()
staffer = Staffer.objects.upgrade_to_staffer(member, nickname)
staffer.save()

print('')
print('Made staffers')

# Add custom fields and gear_types
field_data = {
    "length": {
        "data_type": "float",
        "suffix": "cm",
        "initial": 12.5,
        "label": "length",
        "name": "length",
        "required": True,
        "help_text": "The length of the item"
    },
    "capacity": {
        "data_type": "int",
        "initial": 3,
        "suffix": "person",
        "label": "Number of people",
        "name": "capacity",
        "required": True,
        "help_text": "The number of people that can fit inside",
        "min_value": 0,
        "max_value": 10
    },
    "size": {
        "data_type": "choice",
        "initial": "S",
        "label": "Size",
        "name": "size",
        "required": True,
        "help_text": "The size of the item",
        "choices": (
            ("", "Please choose a size"),
            ("S", "Small"),
            ("M", "Medium"),
            ("L", "Large")
        )
    },
    "manufacturer": {
        "data_type": "string",
        "initial": "Patagonia",
        "label": "Manufacturer",
        "name": "manufacturer",
        "required": True,
        "help_text": "Manufacturer of the item",
        "min_length": 2,
        "max_length": 30
    },
    "is_special": {
        "data_type": "boolean",
        "initial": False,
        "label": "Is special",
        "name": "is_special",
        "required": False,
        "help_text": "Is this a 'special' item?"
    },
    "a_rfid": {
        "data_type": "rfid",
        "initial": "",
        "label": "a rfid to something",
        "name": "a_rfid",
        "required": True,
        "help_text": "Not sure for what, but if you need a rfid"
    },
}
custom_fields = []
for field_name in field_data.keys():
    field = CustomDataField(
        name=field_name,
        data_type=field_data[field_name]['data_type'],
        label=field_data[field_name]['label'],
        required=field_data[field_name]['required'],
        help_text=field_data[field_name]['help_text']
    )
    if 'suffix' in field_data[field_name].keys():
        field.suffix = field_data[field_name]['suffix']
    field.save()
    custom_fields.append(field)

gear_type_names = [
    'Sleeping Bag',
    'Sleeping Pad',
    'Tent',
    'Backpack',
    'Climbing Shoes',
    'Climbing Harness',
    'Skis',
    'Snowboard',
    'Bow',
    'Rope',
    'Helmet',
    'Camping Stove',
    'Cooler',
    'Ski Poles',
    'Ski Boots',
    'Snowboard Boots',
    'Lantern',
    'Water Filter',
    'Crash Pad',
    'Wetsuit',
]
departments = Department.objects.all()
gear_types = []
print("Making Gear Types")
bar = progressbar.ProgressBar()
for name in bar(gear_type_names):
    gear_type = GearType(
        name=name,
        department=pick_random(departments),
    )
    gear_type.save()
    # Add between 1 and 4 custom fields
    for i in range(1, randint(2, 5)):
        gear_type.data_fields.add(pick_random(custom_fields))
    gear_type.save()
    gear_types.append(gear_type)

# Add gear
print('Making Gear...')
number_gear = 120

gear_rfids = []
all_images = list(AlreadyUploadedImage.objects.all())
bar = progressbar.ProgressBar()
for i in bar(range(number_gear)):
    gear_rfid = gen_rfid()
    gear_image = pick_random(all_images)
    authorizer: str = pick_random(staffer_rfids)
    gear_type = pick_random(gear_types)
    transaction, gear = Transaction.objects.add_gear(authorizer, gear_rfid, gear_type, gear_image, **field_data)
    gear_rfids.append(gear_rfid)

print('')
print('Made gear')

# Check out gear to random members
print('Checking out random gear...')
n_gear_to_checkout = int(number_gear / 2)
n_failed_checkouts = 0
bar = progressbar.ProgressBar()
for i in bar(range(n_gear_to_checkout)):
    gear_rfid = pick_random(gear_rfids)
    member_rfid: str = pick_random(member_rfids)
    authorizer: str = pick_random(staffer_rfids)

    try:
        logic.do_checkout(authorizer, member_rfid, gear_rfid)
    except ValidationError as e:
        n_failed_checkouts += 1
print('')
print('{} out of {} checkouts failed to complete'.format(n_failed_checkouts, n_gear_to_checkout))

# Add gear with know RFID
for gear_rfid in RFIDS_TO_HAND_OUT:
    authorizer = '1234567890'
    department = pick_random(departments)
    gear_type = pick_random(gear_types)
    transaction, gear = Transaction.objects.add_gear(authorizer, gear_rfid, gear_type, gear_image, **field_data)
    gear_rfids.append(gear_rfid)

# Check out gear with known RFID
for i in range(5):
    gear_rfid = pick_random(gear_rfids)
    member_rfid = '1234567890'
    authorizer = '1234567890'
    try:
        logic.do_checkout(authorizer, member_rfid, gear_rfid)
    except ValidationError as e:
        pass



print('Finished')
