import setupDjango

from core.models.MemberModels import Member


def get_active_emails():
    active_members = Member.objects.filter(is_active=True)
    emails = [f"{member.email}\n" for member in active_members]

    email_file = open("listserv_emails.txt", 'w')
    email_file.writelines(emails)
    email_file.close()


def update_active_group_based():
    """
    This will update the active/inactive state of all member based on their group, overriding any manual changes
    """
    members_activated = 0
    members_deactivated = 0
    total_active = 0

    for member in Member.objects.all():

        group = member.group.name
        was_active = member.is_active
        if group == "Just Joined" or group == "Expired":
            is_active = False
        else:
            is_active = True
            total_active +=1

        if was_active != is_active:
            if member.is_active:
                members_activated += 1
            else:
                members_deactivated += 1

        member.save()

    print(f"Activated {members_activated}, deactivated {members_deactivated}")
    print(f"New total active members: {total_active}")


if __name__ == "__main__":
    get_active_emails()