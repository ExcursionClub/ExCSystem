from django.contrib.auth.models import Group

from ..models.MemberModels import Member, Staffer
from ..models.GearModels import Gear, GearType, CustomDataField
from ..models.TransactionModels import Transaction
from ..models.CertificationModels import Certification
from ..models.DepartmentModels import Department
from ..models.QuizModels import Question, Answer
from ..models.FileModels import AlreadyUploadedImage

from .MemberAdmin import MemberAdmin, StafferAdmin
from .GearAdmin import GearAdmin, GearTypeAdmin, CustomDataFieldAdmin
from .TransactionAdmin import TransactionAdmin
from .OtherAdmins import CertificationAdmin, DepartmentAdmin, AlreadyUploadedImageAdmin

from core.admin.ExcAdminSite import ExcursionAdmin


admin_site = ExcursionAdmin()

# Register your models here.
admin_site.register(Gear, GearAdmin)
admin_site.register(GearType, GearTypeAdmin)
admin_site.register(CustomDataField, CustomDataFieldAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(Certification, CertificationAdmin)
admin_site.register(Department, DepartmentAdmin)
admin_site.register(AlreadyUploadedImage, AlreadyUploadedImageAdmin)
admin_site.register(Staffer, StafferAdmin)
admin_site.register(Question)
admin_site.register(Answer)
admin_site.register(Group)

# Now register the new MemberAdmin...
admin_site.register(Member, MemberAdmin)
