import setupDjango

from core.models.MemberModels import Member


def get_active_emails():
    members = Member.objects.all()
    emails = [f"{member.email}\n" for member in members if member.is_active_member()]

    with open("listserv_emails.txt", 'w') as email_file:
        email_file.writelines(emails)


if __name__ == "__main__":
    get_active_emails()