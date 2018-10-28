"""
Set the is_active property to be true for all members in the database.

This is useful if you (like i just did) forgot that is_active is used internally by django and needs to be true always
"""

import setupDjango
from core.models.MemberModels import Member

for member in Member.objects.all():
    member.is_active = True
    member.save()
