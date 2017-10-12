import django
import names
import os
import progressbar

from random import randint
from django.db.utils import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ExCSystem.settings")
django.setup()

from core.models.MemberModels import Member, Staffer
from core.models.GearModels import Gear
from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department


admin_rfid = "0000000000"

used_rfids = [admin_rfid]
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
        phone = gen_rfid()
    else:
        used_phones.append(phone)
    return phone


def generate_rand_member():
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    email = "{}.{}@fakeemail.lol".format(first_name, last_name)
    phone = gen_phone()
    rfid = gen_rfid()

    try:
        member = Member.objects.create_member(email, rfid, first_name, last_name, phone, password="fake")
    except IntegrityError:
        member = generate_rand_member()

    return member


# Add the master admin account
admin = Member.objects.create_superuser("admin@excursionclubucsb.org", admin_rfid, "Master", "Admin", gen_phone(), password="admin")


# Add dummy members
print("Making members...")
total_number_members = 100
number_new = int(total_number_members / 5)
number_expired = int(total_number_members / 3)
bar = progressbar.ProgressBar()
for i in bar(range(total_number_members)):

    member = generate_rand_member()
    # Members are made to be new by default
    # After the correct number of new members are made, start making expired members
    if number_new < i < (number_new + number_expired):
        member.status = 2
        member.save()
    # The rest of the members should be active
    else:
        member.status = 1
        member.save()

# Add some staffers
# TODO: Make staffers get generated and added
print("Making staffers...")
number_staffers = 10
bar = progressbar.ProgressBar()
for i in bar(range(number_staffers)):
    member = generate_rand_member()
    nickname = member.first_name + str(i)
    member.save()
    staffer = Staffer.objects.upgrade_to_staffer(member, nickname)
    staffer.save()


# Add certifications
kayak_cert = Certification(title="Kayaking",
                           requirements= "1) Be able to swim god dammit " \
                                         "2) Have received the safety rant, know about wind and current " \
                                         "3) Be able to take the kayak out safely " \
                                         "4) Be able to get off of, flip, and get into a kayak out in the water " \
                                         "5) Be able to bring the kayak back in to shore safely")
kayak_cert.save()

sup_cert = Certification(title="Kayaking",
                         requirements= "1) Be able to swim god dammit " \
                                       "2) Have received the safety rant, know about wind and current "
                                       "3) Be able to take the SUP out safely "
                                       "4) Be able to get off of, flip, and get into a SUP out in the water " \
                                       "5) Be able to bring the SUP back in to shore safely")
sup_cert.save()


# Add departments
departments = ["Camping", "Backpacking", "Rock Climbing", "Skiing/Snowboarding", "Kayaking", "Paddleboarding",
               "Surfing", "Wetsuits", "Mountaineering", "Archery", "Paintballing", "Free Diving", "Off-Road"]
for dept in departments:
    name = dept
    details = "All the gear related to {}".format(name)
    # department = Department()



# Add gear
number_gear = 30
for i in range(number_gear):
    pass