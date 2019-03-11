import sys
from time import sleep
from helper_scripts import setup_django
from core.models.MemberModels import Member

member_email = sys.argv[1]


def wrap_str(start_str, length=20):
    if len(start_str) < length:
        return str(start_str) + (" " * (length - len(start_str)))
    else:
        return str(start_str)


print("Interesting choice to remove a member forever.")
print("Let's see which members you're gonna be brutally destroying...")
sleep(1)

members = Member.objects.filter(email=member_email)
print("Found the following member(s):")
print("---------------------------------------------------------")
for member in members:
    print(
        f"  {wrap_str(member.get_full_name())}  |  {wrap_str(member.email)}  |  {wrap_str(member.group, 12)} "
    )
    print("---------------------------------------------------------")

print(
    "WARNING: This will permanently remove all the members listed above from the database!"
)
print("Are you SURE you want to continue? (yes-fuck-em/no)")
response = input("> ")

if response != "yes-fuck-em":
    print("Yeah, that's probably for the best. Exiting...")
    exit()

print("I do hope you know what you're doing.")
print("Deleting members...")
sleep(2)
members.delete()
print("Done.")
