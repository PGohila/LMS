from django.contrib import admin
from .models import *

admin.site.register(LoanInterestAccrual)
admin.site.register(LoanPenaltiesAccrual)
admin.site.register(LoanAccountEntry)
admin.site.register(LoanRepaymentTry)
admin.site.register(RepaymentEODRetry)
admin.site.register(FailedLoanRepayments)
admin.site.register(PastDueRecord)
admin.site.register(PDActionWorkflowConfig)
admin.site.register(PDNextAction)
admin.site.register(PenaltyAccrual)
admin.site.register(PDCommunicationLog)
admin.site.register(PDLegalAction)
admin.site.register(PDPenaltiesChargesConfig)
admin.site.register(LoanAccountReceivable)
