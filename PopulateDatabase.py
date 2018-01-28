import os
import django
import names
import progressbar

from random import randint

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.timezone import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ExCSystem.settings")
django.setup()

from core.models.MemberModels import Member, Staffer
from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department
from core.models.TransactionModels import Transaction

import kiosk.CheckoutLogic as logic


admin_rfid = "0000000000"
system_rfid = "1111111111"

used_rfids = [admin_rfid, system_rfid]
used_phones = []


def gen_rfid():
    """generates a random and unique rfid"""
    rfid = str(randint(1000000000, 9999999999))
    if rfid in used_rfids:
        rfid = gen_rfid()
    else:
        used_rfids.append(rfid)
    return rfid


def gen_phone():
    """Generates a random and unique phone number"""
    phone = "+{}{}".format(randint(1, 45), randint(1000000, 7000000))
    if phone in used_phones:
        phone = gen_phone()
    else:
        used_phones.append(phone)
    return phone


def gen_duration():
    """Randomly pick a duration of either 90 or 365 days"""
    durations = [timedelta(days=90), timedelta(days=365)]
    return pick_random(durations)


def pick_random(list):
    """Picks and returns a random element from the provided list"""
    return list[randint(0, len(list)-1)]


def generate_rand_member():
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    duration = gen_duration()
    email = "{}.{}@fakeemail.lol".format(first_name, last_name)
    rfid = gen_rfid()

    try:
        member = Member.objects.create_member(email, rfid, membership_duration=duration, password="fake")
        member.first_name = first_name
        member.last_name = last_name
        member.phone_number = gen_phone()
    # If anything goes wrong when making this member, try again
    except IntegrityError:
        member = generate_rand_member()

    return member


# Add the master admin  and excursion system accounts
admin = Member.objects.create_superuser("admin@excursionclubucsb.org", admin_rfid, password="admin")
system = Member.objects.create_member("system@excursionclubucsb.org", system_rfid,
                                      membership_duration=timedelta.max, password="excursion")
Staffer.objects.upgrade_to_staffer(system, "ExCSystem",
                                   "I am the Excursion computer system, and I do all the work nobody else can or wants to do")

# Add dummy members
print("Making members...")
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
        member.status = 2
        member.save()
    # The rest of the members should be active
    else:
        member.status = 1
        member.save()
print("")
print("Made members")

# Add some staffers
print("Making staffers...")
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
print("")
print("Made staffers")

# Add certifications
kayak_cert = Certification(title="Kayaking",
                           requirements= "1) Be able to swim god dammit " \
                                         "2) Have received the safety rant, know about wind and current " \
                                         "3) Be able to take the kayak out safely " \
                                         "4) Be able to get off of, flip, and get into a kayak out in the water " \
                                         "5) Be able to bring the kayak back in to shore safely")
kayak_cert.save()

sup_cert = Certification(title="Stand Up Paddleboarding",
                         requirements= "1) Be able to swim god dammit " \
                                       "2) Have received the safety rant, know about wind and current "
                                       "3) Be able to take the SUP out safely "
                                       "4) Be able to get off of, flip, and get into a SUP out in the water " \
                                       "5) Be able to bring the SUP back in to shore safely")
sup_cert.save()


# Add departments
departments = ["Camping", "Backpacking", "Rock Climbing", "Skiing/Snowboarding", "Kayaking", "Paddleboarding",
               "Surfing", "Wetsuits", "Mountaineering", "Archery", "Paintballing", "Free Diving", "Off-Road"]
all_staffers = Staffer.objects.all()
for dept in departments:
    name = dept
    details = "All the gear related to {}".format(name)
    stl = pick_random(all_staffers)
    department = Department(name=name, description=details)
    department.save()
    department.stls.add(stl)
    department.save()
print("")
print("Made departments")



# Add gear
print("Making Gear...")
number_gear = 120
gear_names = ["Sleeping Bag", "Sleeping Pad", "Tent", "Backpack", "Climbing Shoes", "Climbing Harness", "Skis",
                  "Snowboard", "Bow", "Rope", "Helmet", "Camping Stove", "Cooler", "Ski Poles", "Ski Boots",
                  "Snowboard Boots", "Lantern", "Water Filter", "Crash Pad", "Wetsuit", ]
departments = Department.objects.all()
gear_rfids = []
bar = progressbar.ProgressBar()
for i in bar(range(number_gear)):
    rfid = gen_rfid()
    authorizer = pick_random(staffer_rfids)
    gearname = pick_random(gear_names)
    department = pick_random(departments)  #TODO: Make this not be randomly assigned cause ie skis are not wetsuits

    transaction, gear = Transaction.objects.add_gear(authorizer, rfid, gearname, department)
    gear_rfids.append(rfid)

print("")
print("Made gear")


# Check out gear to random members
print("Checking out random gear...")
n_gear_to_checkout = int(number_gear / 2)
n_failed_checkouts = 0
bar = progressbar.ProgressBar()
for i in bar(range(n_gear_to_checkout)):
    gear_rfid = pick_random(gear_rfids)
    member_rfid = pick_random(member_rfids)
    authorizer = pick_random(staffer_rfids)

    try:
        logic.do_checkout(authorizer, member_rfid, gear_rfid)
    except ValidationError as e:
        n_failed_checkouts += 1
print("")
print("{} out of {} checkouts failed to complete".format(n_failed_checkouts, n_gear_to_checkout))

print("Finished")
