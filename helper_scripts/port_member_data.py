"""Import member data from the old excursion database"""

import os

import progressbar
from core.models.CertificationModels import Certification
from core.models.MemberModels import Member, Staffer, get_profile_pic_upload_location
from django.contrib.auth.models import Group
from django.core.files.images import ImageFile
from django.utils.timezone import datetime
from mysql.connector import connect

skipped_members = []
members_ported = 0

all_staffers = []
staffers_ported = 0
skipped_staffers = []

HOST = "localhost"
USER = "tomek"
PASSWORD = "password"
DB_NAME = "old_excursion"

OLD_PHOTO_DIR = "/home/tomek/Work/Excursion/DataTransfer/OldData/old_member_photos/"

database = connect(host=HOST, user=USER, passwd=PASSWORD, db=DB_NAME)
cursor = database.cursor()

cursor.execute("SELECT * FROM user;")
all_users = cursor.fetchall()

groups = {
    "just joined": Group.objects.get(name="Just Joined"),
    "expired": Group.objects.get(name="Expired"),
    "member": Group.objects.get(name="Member"),
    "staff": Group.objects.get(name="Staff"),
}
kayak_cert = Certification.objects.get(title="Kayaking")
sup_cert = Certification.objects.get(title="Stand Up Paddleboarding")
try:
    bar = progressbar.ProgressBar(redirect_stdout=True)
    for user in bar(all_users):
        old_id = user[0]
        email = user[1]
        phone = (
            "+1" + user[2]
        )  # Current phone numbers are not international, so assume they're US numbers

        cursor.execute(f"SELECT rfid FROM rfid WHERE `table`='user' AND t_id={old_id};")
        try:
            rfid = cursor.fetchall()[0][0]
        except IndexError:
            print(f"Failed to get rfid for {email}! Skipping")
            skipped_members.append(email)
            continue

        full_name_list = user[3].split(" ")
        if full_name_list:
            first_name = full_name_list.pop(0)
            last_name = " ".join(full_name_list)
        else:
            print(f"Skipping {email} because no name was given!")
            skipped_members.append(email)
            continue

        # Get the correct joined and expired dates, and add them to the member
        date_joined = datetime.fromtimestamp(user[6])
        date_expires = datetime.fromtimestamp(user[7])

        # Select which group the member should be placed in
        mem_type = user[4].lower()
        status = user[5].lower()
        if mem_type == "member":
            if status == "new":
                group = groups["just joined"]
            elif status == "expired":
                group = groups["expired"]
            elif status == "active" and date_expires < datetime.now():
                group = groups["expired"]
            elif status == "active" and date_expires > datetime.now():
                group = groups["member"]
        elif (mem_type == "staff" or mem_type == "admin") and status == "active":
            group = groups["staff"]
        else:
            print(f"Failed to classify {email} [{mem_type}, {status}]! Skipping.")
            skipped_members.append(email)
            continue

        # Determine Certifications
        certifications = []
        cursor.execute(f"SELECT * FROM certification WHERE m_id={old_id};")
        old_certs = cursor.fetchall()[0]
        if old_certs[2]:
            certifications.append(sup_cert)
        if old_certs[3]:
            certifications.append(kayak_cert)

        try:
            member = Member.objects.create(
                email=email,
                rfid=rfid,
                group=group,
                phone_number=phone,
                first_name=first_name,
                last_name=last_name,
                date_expires=date_expires,
            )
            member.save()
            member.date_joined = date_joined
            member.certifications.set(certifications)
            member.save()
            members_ported += 1
        except Exception as ex:
            print(f"Failed to create member! {ex}")
            skipped_members.append(email)
            continue

        try:
            # Get the member photo and  prepare it for moving to the server
            old_photo_name = f"{old_id}.jpg"
            old_photo_path = os.path.join(OLD_PHOTO_DIR, old_photo_name)
            if os.path.exists(old_photo_path):
                new_name = get_profile_pic_upload_location(member, old_photo_name)
                photo = ImageFile(open(old_photo_path, "rb"))
                member.picture.save(new_name, photo)
        except Exception as ex:
            print(f"Failed to port photo for {email}! {ex}")

        # If this user is a staffer, make the realted staffer model
        try:
            staff_name = user[10]
            if staff_name:
                all_staffers.append(
                    Staffer.objects.upgrade_to_staffer(member, staff_name)
                )
                staffers_ported += 1
        except Exception as ex:
            print(f"Failed to make {email} into a staffer! {ex}")
            skipped_staffers.append(email)

finally:
    print(f"Ported the data for {members_ported}/{len(all_users)} members!")
    print("Skipped the following members!")
    print(skipped_members)
    print(
        f"Ported data for {staffers_ported} out of {len(all_staffers)} detected staffers!"
    )
    print("Skipped the following staffers")
    print(skipped_staffers)
