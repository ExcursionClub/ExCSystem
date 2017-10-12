from django.contrib import admin
from django.contrib.auth.models import Group

from ..models.MemberModels import Member, Staffer
from ..models.GearModels import Gear
from ..models.TransactionModels import Transaction
from ..models.CertificationModels import Certification
from ..models.DepartmentModels import Department

from .MemberAdmin import MemberAdmin
from .GearAdmin import GearAdmin
from .OtherAdmins import CertificationAdmin, DepartmentAdmin


# Register your models here.
admin.site.register(Gear, GearAdmin)
admin.site.register(Transaction)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Staffer)

# Now register the new MemberAdmin...
admin.site.register(Member, MemberAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)