from django.contrib import admin
from django.contrib.auth.models import Group

from ..models.MemberModels import Member
from ..models.GearModels import Gear
from ..models.TransactionModels import Transaction
from ..models.CertificationModels import Certification
from ..models.DepartamentModels import Departament

from .MemberAdmin import MemberAdmin


# Register your models here.
admin.site.register(Gear)
admin.site.register(Transaction)
admin.site.register(Certification)
admin.site.register(Departament)

# Now register the new MemberAdmin...
admin.site.register(Member, MemberAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)