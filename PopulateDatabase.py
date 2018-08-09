import os
from random import choice, randint
from typing import Any, List, Optional, Union

import django
# Will raise an exception if not run here
# django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExCSystem.settings.development')
django.setup()

import kiosk.CheckoutLogic as logic
import names
import progressbar
from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.MemberModels import Member, Staffer
from core.models.QuizModels import Question, Answer
from core.models.TransactionModels import Transaction
from core.models.GearModels import GearType, CustomDataField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.timezone import timedelta

import buildPermissions

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
    phone = '+{}{}'.format(randint(1, 45), randint(1000000, 9999999))
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


def save_question(question_name=None, question_text=None, choices=None, correct_answer_index=0, error_message="You're Wrong!"):

    # Make and save all of the answers
    answers = []
    for answer in choices:
        ans = Answer(answer_phrase=answer[0], answer_text=answer[1])
        ans.save()
        answers.append(ans)

    # make the question and relate all the answers
    question = Question.objects.create(
        usage="membership",
        name=question_name,
        question_text=question_text,
        correct_answer=answers[correct_answer_index],
        error_message=error_message
    )
    question.answers.add(*answers)
    question.save()

# Build all the groups and permissions
buildPermissions.build_all()

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

# Add certifications
kayak_cert = Certification(
    title='Kayaking', requirements='1) Be able to swim god dammit '
    '2) Have received the safety rant, know about wind and current '
    '3) Be able to take the kayak out safely '
    '4) Be able to get off of, flip, and get into a kayak out in the water '
    '5) Be able to bring the kayak back in to shore safely'
)
kayak_cert.save()

sup_cert = Certification(
    title='Stand Up Paddleboarding', requirements='1) Be able to swim god dammit '
    '2) Have received the safety rant, know about wind and current '
    '3) Be able to take the SUP out safely '
    '4) Be able to get off of, flip, and get into a SUP out in the water '
    '5) Be able to bring the SUP back in to shore safely'
)
sup_cert.save()

# Add departments
departments = [
    'Camping', 'Backpacking', 'Rock Climbing', 'Skiing/Snowboarding', 'Kayaking', 'Paddleboarding',
    'Surfing', 'Wetsuits', 'Mountaineering', 'Archery', 'Paintballing', 'Free Diving', 'Off-Road'
]
all_staffers = Staffer.objects.all()
for dept in departments:
    name = dept
    details = 'All the gear related to {}'.format(name)
    stl: str = pick_random(all_staffers)
    department = Department(name=name, description=details)
    department.save()
    department.stls.add(stl)
    department.save()
print('')
print('Made departments')

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
            ("--", "Please choose a size"),
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
        "initial": None,
        "label": "a rfid to something",
        "name": "a_rfid",
        "required": True,
        "help_text": "Not sure for what, but if you need a rfid"
    },
    "owner": {
        "data_type": "reference",
        "initial": None,
        "label": "Object Owner",
        "name": "owner",
        "required": False,
        "help_text": "The real owner of this item",
        "pk": None,
        "object_type": Staffer,
    },
}
custom_fields = []
for field_name in field_data.keys():
    field = CustomDataField(
        name=field_name,
        data_type=field_data[field_name]['data_type']
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
bar = progressbar.ProgressBar()
for i in bar(range(number_gear)):
    gear_rfid = gen_rfid()
    authorizer: str = pick_random(staffer_rfids)
    gear_type = pick_random(gear_types)
    transaction, gear = Transaction.objects.add_gear(authorizer, gear_rfid, gear_type, **field_data)
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
    transaction, gear = Transaction.objects.add_gear(authorizer, gear_rfid, gear_type, **field_data)
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

print('Writing questions...')

# Write quiz questions
save_question(
    question_name="Punishment",
    question_text="What is the punishment for breaking a club rule?",
    choices=(
        ("wallow", "Wallow in you own incompetence"),
        ("arrest", "We have you arrested"),
        ("membership", "Forfeit your membership"),
        ("lashes", "10 lashes before the mast")
    ),
    correct_answer_index=2,
    error_message="If you break a rule you lose your membership!"
)
save_question(
    question_name="gear",
    question_text="How many of each item type can you check out?",
    choices=(
        ("None", "Trick question, we don't check out gear"),
        ("1", "One of each type of gear"),
        ("2", "Two of each type of gear"),
        ("unlimited", "as many as you'd like")

    ),
    correct_answer_index=1,
    error_message="You can only check out one of each type of item!"
)
save_question(
    question_name="certification",
    question_text="How do you get certified for kayaks and SUPS?",
    choices=(
        ("class", "Take a $500 class"),
        ("trip", "Go on a trip with a staffer"),
        ("date", "Bang a bunch of staffers"),
        ("nudie", "Run naked around the block")
    ),
    correct_answer_index=1,
    error_message="To get certified just go on a trip with a staffer."
)
save_question(
    question_name="broken",
    question_text="What do you do when a piece of gear breaks?",
    choices=(
        ("hide", "Hide it and hope no one notices"),
        ("run", "Run away, Simba! Run away and NEVER return!"),
        ("fine", "Pay a $10 fine for broken gear"),
        ("tell", "Shit happens. Just let us know so we can fix it")
    ),
    correct_answer_index=3,
    error_message="Just tell us it's broken so we can make sure it stays in good shape."
)
save_question(
    question_name="staffers",
    question_text="Who are our staffers?",
    choices=(
        ("volunteers", "Student volunteers who do this for fun"),
        ("pros", "Well-paid professionals"),
        ("blokes", "Random blokes we found on the street"),
        ("fake", "Fake news. There are no staffers")
    ),
    correct_answer_index=0,
    error_message="All our staffers are volunteers!"
)

print('Finished')
