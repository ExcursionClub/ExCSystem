"""Import member data from the old excursion database"""

import setupDjango

from mysql.connector import connect
from django.utils.timezone import datetime, timedelta
from django.contrib.auth.models import Group
from core.models.CertificationModels import Certification

from core.models.MemberModels import Member

skipped_members = []
members_ported = 0

HOST = "localhost"
USER = "tomek"
PASSWORD = "password"
DB_NAME = "old_excursion"

database = connect(host=HOST, user=USER, passwd=PASSWORD, db=DB_NAME)
cursor = database.cursor()

cursor.execute("SELECT * FROM user WHERE date_expires > 1420760194;")
all_users = cursor.fetchall()

groups = {
    "just joined": Group.objects.get(name="Just Joined"),
    "expired": Group.objects.get(name="Expired"),
    "member": Group.objects.get(name="Member"),
    "staff": Group.objects.get(name="Staff"),
}
kayak_cert = Certification.objects.get(title='Kayaking')
sup_cert = Certification.objects.get(title='Stand Up Paddleboarding')
try:
    for user in all_users:
        old_id = user[0]
        email = user[1]
        phone = user[2]

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
        if mem_type == "member" and status == "new":
            group = groups["just joined"]
        elif mem_type == "member" and status == "expired":
            group = groups["expired"]
        elif mem_type == "member" and status == "active" and date_expires < datetime.now():
            group = groups["expired"]
        elif mem_type == "member" and status == "active" and date_expires > datetime.now():
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
                date_joined=date_joined,
                date_expires=date_expires,
            )
            member.save()
            member.certifications.set(certifications)
            member.save()
            members_ported += 1
        except Exception as ex:
            print(f"Failed to create member! {ex}")
            skipped_members.append(email)
            continue


finally:
    print(f"Ported the data for {members_ported} members!")
    print("Skipped the following members!")
    print(skipped_members)



    

