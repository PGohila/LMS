from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from .models import *
from .serializers import *
from django.db.models import Sum, F
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from decimal import Decimal
from django.utils import timezone
from rest_framework import generics
from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Welcome to the Loan Management API</h1><p>Visit /swagger/ for API documentation.</p>")

# manageing CRUD operations for company
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

# ================================ Customer Management: ==========================
# Manages customer CRUD operations.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# Manage customer profiles and related information.
# 	Actions: Create and update customer profiles.
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return CustomerProfile.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()

# Manages identity verification for customers.
class IdentityVerificationViewSet(viewsets.ModelViewSet):
    queryset = IdentityVerification.objects.all()
    serializer_class = IdentityVerificationSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return IdentityVerification.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()

# Perform credit assessments for customers.
# 	Actions: Create and view credit assessments.
# Handles credit assessments for customers.
class CreditAssessmentViewSet(viewsets.ModelViewSet):
    queryset = CreditAssessment.objects.all()
    serializer_class = CreditAssessmentSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return CreditAssessment.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()

# Tracks credit history for customers.
class CreditHistoryViewSet(viewsets.ModelViewSet):
    queryset = CreditHistory.objects.none()
    serializer_class = CreditHistorySerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return CreditHistory.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()

# Track communications with customers.
# 	Actions: Create and manage communication logs.
class CustomerCommunicationViewSet(viewsets.ModelViewSet):
    queryset = CustomerCommunication.objects.all()
    serializer_class = CustomerCommunicationSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return CustomerCommunication.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()


#======================================= Loan Management ===========================

# A customer applies for a loan.(same time it will save ReusableLoanCalculator and LoanSchedule )
class LoanApplicationViewSet(viewsets.ModelViewSet):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return LoanApplication.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()

    # Methods for calculate-interest, calculate-loan, and generate-statement remain unchanged

# Handles listing and creation of loan
class LoanListCreateView(generics.ListCreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


# Handles retrieving, updating, and destroying loan details
class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

# Loan applications are reviewed and approved
# Update loan application status, generate repayment schedules.
class LoanApprovalViewSet(viewsets.ModelViewSet):
    queryset = LoanApplication.objects.filter(status__in=['submitted', 'under_review'])
    serializer_class = LoanApprovalSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        # Call the serializer's update method, which will handle approval and repayment schedule generation
        serializer.save()


# Approved loans are disbursed to the customer.
# Create a new disbursement record.
class DisbursementViewSet(viewsets.ModelViewSet):
    queryset = Disbursement.objects.all()
    serializer_class = DisbursementSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return Disbursement.objects.filter(loan_application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()


# Repayment schedules are created for approved loans.
# Create repayment schedules based on loan terms.
class RepaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = RepaymentSchedule.objects.all()
    serializer_class = RepaymentScheduleSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return RepaymentSchedule.objects.filter(
                loan_application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

    @action(detail=True, methods=['get'], url_path='total-due')
    def total_due(self, request, pk=None):
        agreement = self.get_object()
        total_due = agreement.repaymentschedule_set.aggregate(
            total=Sum(F('principal_amount') + F('interest_amount'))
        )['total']

        return Response({'total_due': total_due}, status=status.HTTP_200_OK)



# Loan account filters
class LoanAccountFilter(FilterSet):
    balance = NumberFilter(field_name="balance", lookup_expr='exact')
    balance__gt = NumberFilter(field_name="balance", lookup_expr='gt')
    balance__lt = NumberFilter(field_name="balance", lookup_expr='lt')
    balance__gte = NumberFilter(field_name="balance", lookup_expr='gte')
    balance__lte = NumberFilter(field_name="balance", lookup_expr='lte')
    balance__range = NumberFilter(field_name="balance", lookup_expr='range')

    class Meta:
        model = LoanAccount
        fields = ['balance']

# Customers make payments against their loans.
# 	Custom Action: repay_loan
# 	Apply payment to accrued penalties.
# 	Apply remaining amount to pending repayment schedules.
# 	Update loan account and repayment schedules.

class LoanAccountViewSet(viewsets.ModelViewSet):
    queryset = LoanAccount.objects.all()
    serializer_class = LoanAccountSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LoanAccountFilter
    ordering_fields = ['balance']
    ordering = ['balance']

    @action(detail=True, methods=['post'], url_path='repay-loan')
    def repay_loan(self, request, pk=None): # This method handles the repayment of a loan.
        loan_account = self.get_object()
    
        amount = Decimal(request.data.get('amount', 0))

        # Apply penalties first
        if loan_account.accrued_penalty > 0:
            if amount >= loan_account.accrued_penalty:
                amount -= loan_account.accrued_penalty
                loan_account.accrued_penalty = Decimal('0.00')
            else:
                loan_account.accrued_penalty -= amount
                amount = Decimal('0.00')

        # Apply to the next due repayment schedule
        schedules = RepaymentSchedule.objects.filter(loan_application=loan_account.loan_application,
                                                     status='pending').order_by('due_date')
        for schedule in schedules:
            if amount <= 0:
                break
            if amount >= schedule.total_amount:
                amount -= schedule.total_amount
                schedule.status = 'paid'
            else:
                loan_account.advance_payment_balance += amount
                amount = Decimal('0.00')
            schedule.save()

        # If there's any remaining amount, add to advance payment balance
        if amount > 0:
            loan_account.advance_payment_balance += amount

        loan_account.save()

        return Response({"status": "Repayment processed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='apply-advance-payment')
    def apply_advance_payment(self, request, pk=None):
        loan_account = self.get_object()
        schedules = RepaymentSchedule.objects.filter(loan_application=loan_account.loan_application,status='pending').order_by('due_date')                                    
        for schedule in schedules:
            if loan_account.advance_payment_balance <= 0:
                break
            if loan_account.advance_payment_balance >= schedule.total_amount:
                loan_account.advance_payment_balance -= schedule.total_amount
                schedule.status = 'paid'
            else:
                schedule.status = 'partial'
                schedule.total_amount -= loan_account.advance_payment_balance
                loan_account.advance_payment_balance = Decimal('0.00')
            schedule.save()

        loan_account.save()

        return Response({"status": "Advance payment applied successfully."}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'id' in self.request.query_params:
            return queryset.filter(id=self.request.query_params['id'])
        return queryset

    # Methods for disburse_funds, repay_loan, create_transaction, apply_repayment remain unchanged

# Track the status and performance of loans.
# View and update loan monitoring records.
class LoanMonitoringViewSet(viewsets.ModelViewSet):
    queryset = LoanMonitoring.objects.all()
    serializer_class = LoanMonitoringSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return LoanMonitoring.objects.filter(
                schedule__loan_application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Settling loan accounts after full repayment or other conditions.
# 	Custom Actions: complete_settlement, accept_settlement, reject_settlement
# 	Update settlement status and related details.

class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer

    def get_queryset(self):
        loan_application_id = self.request.query_params.get('loan_application_id')
        if loan_application_id:
            return Settlement.objects.filter(account_id=loan_application_id)
        return Settlement.objects.all()

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_settlement(self, request, pk=None):
        settlement = self.get_object()
        if settlement.status != 'accepted':
            return Response({"error": "Settlement must be accepted before it can be completed."},
                            status=status.HTTP_400_BAD_REQUEST)

        settlement.status = 'completed'
        settlement.settlement_date = timezone.now()
        settlement.save()

        # Optionally, close the loan account or perform other actions here

        return Response({"status": "Settlement completed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept_settlement(self, request, pk=None):
        settlement = self.get_object()
        if settlement.status != 'pending':
            return Response({"error": "Only pending settlements can be accepted."},
                            status=status.HTTP_400_BAD_REQUEST)

        settlement.status = 'accepted'
        settlement.save()

        return Response({"status": "Settlement accepted."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_settlement(self, request, pk=None):
        settlement = self.get_object()
        if settlement.status != 'pending':
            return Response({"error": "Only pending settlements can be rejected."},
                            status=status.HTTP_400_BAD_REQUEST)

        settlement.status = 'rejected'
        settlement.save()

        return Response({"status": "Settlement rejected."}, status=status.HTTP_200_OK)



# Update loan terms or conditions.
# Create loan modification records.
class LoanModificationViewSet(viewsets.ModelViewSet):
    queryset = LoanModification.objects.all()
    serializer_class = LoanModificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Set the modified_by field to the current user and create the modification
        serializer.save(modified_by=self.request.user.username)

# Manages restructuring of loans.
class LoanRestructuringViewSet(viewsets.ModelViewSet):
    queryset = LoanRestructuring.objects.all()
    serializer_class = LoanRestructuringSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return LoanRestructuring.objects.filter(application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Handles loan agreements and related signatures.
class LoanAgreementViewSet(viewsets.ModelViewSet):
    queryset = LoanAgreement.objects.all()
    serializer_class = LoanAgreementSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return LoanAgreement.objects.filter(application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Manages signatures related to loan agreements
class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer

    def get_queryset(self):
        if 'loan_agreement_id' in self.request.query_params:
            return Signature.objects.filter(agreement_id=self.request.query_params['loan_agreement_id'])
        return super().get_queryset()

# ============================== Penalties and Collections ======================


# past Dues Processing -----
# Track and process past due records and penalties.
# 	Actions: Manage records and workflows for past due loans.
class PastDueRecordViewSet(viewsets.ModelViewSet):
    queryset = PastDueRecord.objects.all()
    serializer_class = PastDueRecordSerializer

#  Manages penalty accruals.
class PenaltyAccrualViewSet(viewsets.ModelViewSet):
    queryset = PenaltyAccrual.objects.all()
    serializer_class = PenaltyAccrualSerializer

# Manages past due action workflows.
class PDActionWorkflowConfigViewSet(viewsets.ModelViewSet):
    queryset = PDActionWorkflowConfig.objects.all()
    serializer_class = PDActionWorkflowConfigSerializer

# Manages next actions in past due workflows.
class PDNextActionViewSet(viewsets.ModelViewSet):
    queryset = PDNextAction.objects.all()
    serializer_class = PDNextActionSerializer

# Logs communications related to past due loans.
class PDCommunicationLogViewSet(viewsets.ModelViewSet):
    queryset = PDCommunicationLog.objects.all()
    serializer_class = PDCommunicationLogSerializer

#  Manages legal actions for past due loans.
class PDLegalActionViewSet(viewsets.ModelViewSet):
    queryset = PDLegalAction.objects.all()
    serializer_class = PDLegalActionSerializer

# Manages penalties and charges configurations for past due loans
class PDPenaltiesChargesConfigViewSet(viewsets.ModelViewSet):
    queryset = PDPenaltiesChargesConfig.objects.all()
    serializer_class = PDPenaltiesChargesConfigSerializer

# Manages collections for past due loans
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return Collection.objects.filter(account_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Manages retention offers for customers.  
class RetentionOfferViewSet(viewsets.ModelViewSet):
    queryset = RetentionOffer.objects.all()
    serializer_class = RetentionOfferSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return RetentionOffer.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()


# Tracks metrics related to customer retention.
class RetentionMetricViewSet(viewsets.ModelViewSet):
    queryset = RetentionMetric.objects.all()
    serializer_class = RetentionMetricSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return RetentionMetric.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()


# ============================ Financial Management: ========================

# want to filter details
class AccountFilter(FilterSet):
    balance = NumberFilter(field_name="balance", lookup_expr='exact')
    balance__gt = NumberFilter(field_name="balance", lookup_expr='gt')
    balance__lt = NumberFilter(field_name="balance", lookup_expr='lt')
    balance__gte = NumberFilter(field_name="balance", lookup_expr='gte')
    balance__lte = NumberFilter(field_name="balance", lookup_expr='lte')
    balance__range = NumberFilter(field_name="balance", lookup_expr='range')
    account_name = CharFilter(field_name="account_name", lookup_expr='icontains')
    account_type = CharFilter(field_name="account_type", lookup_expr='exact')

    class Meta:
        model = Account
        fields = ['account_name', 'account_type', 'balance']

# Manages financial accounts with filtering and ordering options
class AccountViewSet(viewsets.ModelViewSet): #  viewsets.ModelViewSet, which provides a full set of CRUD
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter] # 1. DjangoFilterBackend: Allows for filtering using Django Filter, 2. SearchFilter: Enables searching within specified fields., 3. OrderingFilter: Allows ordering the results based on specified fields.
    filterset_class = AccountFilter 
    search_fields = ['account_name', 'account_type']
    ordering_fields = ['balance', 'account_name', 'account_type']
    ordering = ['account_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'id' in self.request.query_params:
            return queryset.filter(id=self.request.query_params['id'])
        return queryset

# Manages the register of due payments.
class DueRegisterViewSet(viewsets.ModelViewSet):
    queryset = DueRegister.objects.all()
    serializer_class = DueRegisterSerializer

    def get_queryset(self):
        if 'loan_id' in self.request.query_params:
            return DueRegister.objects.filter(loan_account_id=self.request.query_params['loan_id'])
        return super().get_queryset()
    
# Handles transactions related to accounts.

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        if 'account_id' in self.request.query_params:
            return Transaction.objects.filter(account_id=self.request.query_params['account_id'])
        return super().get_queryset()

# Manages records of paid items against dues.
class PaidItemViewSet(viewsets.ModelViewSet):
    queryset = PaidItem.objects.all()
    serializer_class = PaidItemSerializer

    def get_queryset(self):
        if 'due_register_id' in self.request.query_params:
            return PaidItem.objects.filter(due_register_id=self.request.query_params['due_register_id'])
        return super().get_queryset()

# Manages loan accounts receivable.
class LoanAccountReceivableViewSet(viewsets.ModelViewSet):
    queryset = LoanAccountReceivable.objects.all()
    serializer_class = LoanAccountReceivableSerializer

# Handles loan reporting
class LoanReportViewSet(viewsets.ModelViewSet):
    queryset = LoanReport.objects.all()
    serializer_class = LoanReportSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return LoanReport.objects.filter(application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Manages balance adjustments in loan accounts
class BalanceAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = BalanceAdjustment.objects.all()
    serializer_class = BalanceAdjustmentSerializer

    def get_queryset(self):
        if 'repayment_schedule_id' in self.request.query_params:
            return BalanceAdjustment.objects.filter(schedule_id=self.request.query_params['repayment_schedule_id'])
        return super().get_queryset()


# =================================== Loan calculater ========================

# API endpoint for calculating loan repayment schedules

class LoanCalculatorView(APIView):
    """
    API endpoint that allows users to calculate loan repayment schedules.
    """

    def get(self, request, *args, **kwargs):
        # Return empty data for form fields
        serializer = LoanCalculatorSerializer()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = LoanCalculatorSerializer(data=request.data)
        if serializer.is_valid():
            repayment_schedule = serializer.calculate_repayment_schedule(serializer.validated_data)
            return Response(repayment_schedule, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#=================================== Documentation and Verification ==================================

# Handle documents related to loans and customer identity.
# 	Actions: Create, retrieve, and manage documents.
# Manages documents related to loans and customer identity
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return Document.objects.filter(loan_application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

# Manages types of document
class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [AllowAny]

# Handles fraud checks during the loan process
class FraudCheckViewSet(viewsets.ModelViewSet):
    queryset = FraudCheck.objects.all()
    serializer_class = FraudCheckSerializer

    def get_queryset(self):
        # Customize the queryset if needed
        return super().get_queryset()

# Manages employment verification for customers
class EmploymentVerificationViewSet(viewsets.ModelViewSet):
    queryset = EmploymentVerification.objects.all()
    serializer_class = EmploymentVerificationSerializer

    def get_queryset(self):
        if 'customer_id' in self.request.query_params:
            return EmploymentVerification.objects.filter(customer_id=self.request.query_params['customer_id'])
        return super().get_queryset()
    
# ============================================ Loan Officer Management ==============================
# Manages loan officers.
class LoanOfficerViewSet(viewsets.ModelViewSet):
    queryset = LoanOfficer.objects.all()
    serializer_class = LoanOfficerSerializer

# Manages reviews of loan officers.
class LoanOfficerReviewViewSet(viewsets.ModelViewSet):
    queryset = LoanOfficerReview.objects.all()
    serializer_class = LoanOfficerReviewSerializer

    def get_queryset(self):
        if 'loan_application_id' in self.request.query_params:
            return LoanOfficerReview.objects.filter(application_id=self.request.query_params['loan_application_id'])
        return super().get_queryset()

#============================== Reminders and Notifications =========================
# Manages reminders related to repayment schedules.
class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer

    def get_queryset(self):
        if 'repayment_schedule_id' in self.request.query_params:
            return Reminder.objects.filter(schedule_id=self.request.query_params['repayment_schedule_id'])
        return super().get_queryset()

# Handles payments related to repayment schedules
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if 'repayment_schedule_id' in self.request.query_params:
            return Payment.objects.filter(schedule_id=self.request.query_params['repayment_schedule_id'])
        return super().get_queryset()

# Manages late payments.

class LatePaymentViewSet(viewsets.ModelViewSet):
    queryset = LatePayment.objects.all()
    serializer_class = LatePaymentSerializer

    def get_queryset(self):
        if 'repayment_schedule_id' in self.request.query_params:
            return LatePayment.objects.filter(schedule_id=self.request.query_params['repayment_schedule_id'])
        return super().get_queryset()

#============================================================================================================


class LoanApplicationViewSet(viewsets.ModelViewSet):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanApplication.objects.none()  # Empty queryset during schema generation
        return super().get_queryset()
