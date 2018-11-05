import setupDjango

from core.models.MemberModels import Member


def get_active_emails():
    members = Member.objects.all()
    emails = [f"{member.email}\n" for member in members if member.is_active_member]
    return emails


def write_emails(email_list):
    with open("listserv_emails.txt", 'w') as email_file:
        email_file.writelines(email_list)


if __name__ == "__main__":
    get_active_emails()
