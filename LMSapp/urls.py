from django.urls import include, path, reverse
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the router
router = DefaultRouter()

# Register viewsets with the router
router.register(r'companies', views.CompanyViewSet)
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'loan_accounts', views.LoanAccountViewSet, basename='loan_account')
router.register(r'customers', views.CustomerViewSet)
router.register(r'loan_applications', views.LoanApplicationViewSet)
router.register(r'document-types', views.DocumentTypeViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'identity_verifications', views.IdentityVerificationViewSet)
router.register(r'credit_histories', views.CreditHistoryViewSet)
router.register(r'fraud_checks', views.FraudCheckViewSet, basename='fraud_check')
router.register(r'employment_verifications', views.EmploymentVerificationViewSet)
router.register(r'loan_officers', views.LoanOfficerViewSet)
router.register(r'loan_officer_reviews', views.LoanOfficerReviewViewSet)
router.register(r'loan_agreements', views.LoanAgreementViewSet)
router.register(r'signatures', views.SignatureViewSet)
router.register(r'disbursements', views.DisbursementViewSet)
router.register(r'repayment_schedules', views.RepaymentScheduleViewSet)
router.register(r'reminders', views.ReminderViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'late_payments', views.LatePaymentViewSet)
router.register(r'balance_adjustments', views.BalanceAdjustmentViewSet)
router.register(r'loan_monitorings', views.LoanMonitoringViewSet)
router.register(r'loan_restructurings', views.LoanRestructuringViewSet)
router.register(r'collections', views.CollectionViewSet)
router.register(r'settlements', views.SettlementViewSet, basename='settlement')
router.register(r'loan_reports', views.LoanReportViewSet)
router.register(r'customer_profiles', views.CustomerProfileViewSet)
router.register(r'credit_assessments', views.CreditAssessmentViewSet)
router.register(r'customer_communications', views.CustomerCommunicationViewSet)
router.register(r'retention_offers', views.RetentionOfferViewSet)
router.register(r'retention_metrics', views.RetentionMetricViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'due-register', views.DueRegisterViewSet)
router.register(r'paid-items', views.PaidItemViewSet)

router.register(r'loan-approvals', views.LoanApprovalViewSet, basename='loan-approval')


# Define urlpatterns, adding the LoanCalculatorView separately
urlpatterns = [
    path('', include(router.urls)),
    path('loan-calculator/', views.LoanCalculatorView.as_view(), name='loan-calculator'),
]
