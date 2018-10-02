import setupDjango

from core.models.MemberModels import Member

active_members = Member.objects.filter(is_active=True)
emails = [member.email for member in active_members]

email_file = open("listserv_emails.txt", 'w')
email_file.writelines(emails)
email_file.close()