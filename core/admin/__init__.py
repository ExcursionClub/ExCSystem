from django.contrib import admin
from django.contrib.auth.models import Group

from ..models.MemberModels import Member, Staffer
from ..models.GearModels import Gear
from ..models.TransactionModels import Transaction
from ..models.CertificationModels import Certification
from ..models.DepartmentModels import Department
from ..models.QuizModels import Question, Answer

from .MemberAdmin import MemberAdmin, StafferAdmin
from .GearAdmin import GearAdmin
from .TransactionAdmin import TransactionAdmin
from .OtherAdmins import CertificationAdmin, DepartmentAdmin


# Register your models here.
admin.site.register(Gear, GearAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Staffer, StafferAdmin)
admin.site.register(Question)
admin.site.register(Answer)

# Now register the new MemberAdmin...
admin.site.register(Member, MemberAdmin)