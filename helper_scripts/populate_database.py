"""Populate the database with a complete set of randomly generated data"""
import helper_scripts.setup_django
import os
from random import choice, randint
from typing import Any, List, Optional

from helper_scripts import build_basic_data
import kiosk.CheckoutLogic as logic
import names
import progressbar
from phonenumbers import data, is_valid_number, parse
from core.models.DepartmentModels import Department
from core.models.FileModels import AlreadyUploadedImage
from core.models.GearModels import CustomDataField, GearType
from core.models.MemberModels import Member, Staffer
from core.models.TransactionModels import Transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.timezone import timedelta

build_basic_data.build_all()

ADMIN_RFID = "0000000000"
SYSTEM_RFID = "1111111111"
PASSWORD = os.environ.get("PASSWORD")
PHONE_PREFIXES = list(data._COUNTRY_CODE_TO_REGION_CODE.keys())

used_rfids = [ADMIN_RFID, SYSTEM_RFID]
used_phones: List[Optional[str]] = []

RFIDS_TO_HAND_OUT = [
    "1000000000",
    "2000000000",
    "3000000000",
    "4000000000",
    "5000000000",
    "6000000000",
    "7000000000",
]


def gen_rfid() -> str:
    """generates a random and unique rfid"""
    rfid = str(randint(1_000_000_000, 9_999_999_999))
    if rfid in used_rfids:
        rfid = gen_rfid()
    else:
        used_rfids.append(rfid)
    return rfid


def gen_phone_num() -> str:
    """Generates a random and unique phone number"""
    phone = "+1 (909) {local}".format(country=choice(PHONE_PREFIXES), local=randint(100_0000, 999_9999))
    phone_obj = parse(phone)
    valid = is_valid_number(phone_obj)
    if not valid:
        is_valid_number(phone_obj)
        phone = gen_phone_num()
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


def generate_member() -> Member:
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
    except IntegrityError:
        # If anything goes wrong when making this member, try again
        random_member = generate_member()

    return random_member


# Add the master admin  and excursion system accounts
try:
    admin = Member.objects.create_superuser(
        "admin@climbingclubuw.org", ADMIN_RFID, password=PASSWORD
    )
except IntegrityError:
    pass  # If admin already exists don't try to re-make it
try:
    system = Member.objects.create_member(
        "s@e.org", SYSTEM_RFID, membership_duration=timedelta.max, password=PASSWORD
    )
except IntegrityError:
    pass  # If system already exists don't try to re-make it
else:
    Staffer.objects.upgrade_to_staffer(
        system,
        "uwccsystem",
        "I am the Climbing Club computer system, and I do all the work nobody else can or wants to do",
    )


# Add dummy members
print("Making members...")
total_number_members = 20
number_new = int(total_number_members / 5)
number_expired = int(total_number_members / 3)
member_rfids = []
bar = progressbar.ProgressBar()
for i in bar(range(total_number_members)):

    member = generate_member()
    member_rfids.append(member.rfid)
    # Members are made to be new by default
    # After the correct number of new members are made, start making expired members
    if number_new < i < (number_new + number_expired):
        member.expire()
        member.save()
    # The rest of the members should be active
    elif i > (number_new + number_expired):
        member.promote_to_active()
        member.save()
print("")
print("Made members")

# Add some staffers
print("Making staffers...")
number_staffers = 5
staffer_rfids = []
bar = progressbar.ProgressBar()
for i in bar(range(number_staffers)):
    member = generate_member()
    member_rfids.append(member.rfid)
    staffer_rfids.append(member.rfid)
    nickname = member.first_name + str(i)
    member.save()
    staffer = Staffer.objects.upgrade_to_staffer(member, nickname)
    staffer.is_active = choice([0, 1])
    staffer.save()

# Add staffer with known rfid
try:
    member = generate_member()
    member.rfid = 1_234_567_890
    member_rfids.append(member.rfid)
    staffer_rfids.append(member.rfid)
    nickname = member.first_name + "RFIDKnown"
    member.save()
    staffer = Staffer.objects.upgrade_to_staffer(member, nickname)
    staffer.save()
except IntegrityError as ex:
    print('Member with known RFID already exists! Skipping')

print("")
print("Made staffers")

# Add custom fields and geartypes
field_data = {
    "length": {
        "data_type": "float",
        "suffix": "cm",
        "initial": 12.5,
        "label": "length",
        "name": "length",
        "required": True,
        "help_text": "The length of the item",
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
        "max_value": 10,
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
            ("L", "Large"),
        ),
    },
    "manufacturer": {
        "data_type": "string",
        "initial": "Patagonia",
        "label": "Manufacturer",
        "name": "manufacturer",
        "required": True,
        "help_text": "Manufacturer of the item",
        "min_length": 2,
        "max_length": 30,
    },
    "is_special": {
        "data_type": "boolean",
        "initial": False,
        "label": "Is special",
        "name": "is_special",
        "required": False,
        "help_text": "Is this a 'special' item?",
    },
    "a_rfid": {
        "data_type": "rfid",
        "initial": "",
        "label": "a rfid to something",
        "name": "a_rfid",
        "required": True,
        "help_text": "Not sure for what, but if you need a rfid",
    },
}
custom_fields = []
for field_name in field_data.keys():
    field = CustomDataField(
        name=field_name,
        data_type=field_data[field_name]["data_type"],
        label=field_data[field_name]["label"],
        required=field_data[field_name]["required"],
        help_text=field_data[field_name]["help_text"],
    )
    if "suffix" in field_data[field_name].keys():
        field.suffix = field_data[field_name]["suffix"]
    try:
        field.save()
    except IntegrityError as ex:
        print(f'Custom data field {field_name} already exists!')
        field = CustomDataField.objects.get(name=field_name)
    custom_fields.append(field)

geartype_names = [
    "Sleeping Bag",
    "Sleeping Pad",
    "Tent",
    "Backpack",
    "Climbing Shoes",
    "Climbing Harness",
    "Skis",
    "Snowboard",
    "Bow",
    "Rope",
    "Helmet",
    "Camping Stove",
    "Cooler",
    "Ski Poles",
    "Ski Boots",
    "Snowboard Boots",
    "Lantern",
    "Water Filter",
    "Crash Pad",
    "Wetsuit",
]
departments = Department.objects.all()
geartypes = []
print("Making Gear Types")
bar = progressbar.ProgressBar()
for name in bar(geartype_names):
    geartype = GearType(name=name, department=pick_random(departments))
    geartype.save()
    # Add between 1 and 4 custom fields
    for i in range(1, randint(2, 5)):
        geartype.data_fields.add(pick_random(custom_fields))
    geartype.save()
    geartypes.append(geartype)

# Add gear
print("Making Gear...")
number_gear = 60

gear_rfids = []
all_gear_images = list(AlreadyUploadedImage.objects.all())
# TODO: Select shaka if no gear image is uploaded or chosen
bar = progressbar.ProgressBar()
for i in bar(range(number_gear)):
    gear_rfid = gen_rfid()
    authorizer: str = pick_random(staffer_rfids)
    geartype = pick_random(geartypes)

    transaction, gear = Transaction.objects.add_gear(
        authorizer_rfid=authorizer,
        gear_rfid=gear_rfid,
        geartype=geartype,
        gear_image=pick_random(all_gear_images),
        **field_data,
    )
    gear_rfids.append(gear_rfid)

print("")
print("Made gear")

# Check out gear to random members
print("Checking out random gear...")
gear_to_checkout = int(number_gear / 2)
failed_checkouts = 0
bar = progressbar.ProgressBar()
for i in bar(range(gear_to_checkout)):
    gear_rfid = pick_random(gear_rfids)
    member_rfid: str = pick_random(member_rfids)
    authorizer: str = pick_random(staffer_rfids)

    try:
        logic.do_checkout(authorizer, member_rfid, gear_rfid)
    except ValidationError as e:
        failed_checkouts += 1
print("")
print(f"{failed_checkouts} out of {gear_to_checkout} checkouts failed to complete")

# Add gear with know RFID
for gear_rfid in RFIDS_TO_HAND_OUT:
    authorizer = "1234567890"
    department = pick_random(departments)
    gear_type = pick_random(geartypes)
    try:
        transaction, gear = Transaction.objects.add_gear(
            authorizer,
            gear_rfid,
            gear_type,
            gear_image=pick_random(all_gear_images),
            **field_data,
        )
    except (IntegrityError, ValidationError) as ex:
        pass
    gear_rfids.append(gear_rfid)

# Check out gear with known RFID
for i in range(5):
    gear_rfid = pick_random(gear_rfids)
    member_rfid = "1234567890"
    authorizer = "1234567890"
    try:
        logic.do_checkout(authorizer, member_rfid, gear_rfid)
    except ValidationError as e:
        pass


print("Finished")
