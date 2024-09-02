from rest_framework import serializers
from decimal import Decimal, getcontext
from .models import *
from django.utils import timezone


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = '__all__'


class LoanAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAccount
        fields = '__all__'


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class DueRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DueRegister
        fields = '__all__'


class PaidItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaidItem
        fields = '__all__'


class RepaymentPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentPriority
        fields = '__all__'


class LoanStatementSerializer(serializers.Serializer):
    loan_application_id = serializers.IntegerField()

    def generate_statement(self):
        loan_application = LoanApplication.objects.get(pk=self.validated_data['loan_application_id'])
        repayments = RepaymentSchedule.objects.filter(loan_application=loan_application).order_by('due_date')

        statement = []
        for repayment in repayments:
            statement.append({
                'installment_number': repayment.installment_number,
                'due_date': repayment.due_date,
                'principal_amount': repayment.principal_amount,
                'interest_amount': repayment.interest_amount,
                'total_amount': repayment.total_amount,
                'status': repayment.status,
            })

        return statement


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'  # Include all fields except owner, which has been removed


class IdentityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = '__all__'


class CreditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditHistory
        fields = '__all__'


class FraudCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudCheck
        fields = '__all__'


class EmploymentVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentVerification
        fields = '__all__'


class LoanOfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanOfficer
        fields = '__all__'


class LoanOfficerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanOfficerReview
        fields = '__all__'


class LoanAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAgreement
        fields = '__all__'


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'


class DisbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disbursement
        fields = '__all__'


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class LatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatePayment
        fields = '__all__'


class BalanceAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceAdjustment
        fields = '__all__'


class LoanMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanMonitoring
        fields = '__all__'


class LoanRestructuringSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRestructuring
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'


class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = '__all__'


class LoanReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanReport
        fields = '__all__'


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'


class CreditAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditAssessment
        fields = '__all__'


class CustomerCommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCommunication
        fields = '__all__'


class RetentionOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionOffer
        fields = '__all__'


class RetentionMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionMetric
        fields = '__all__'


class LoanCalculatorSerializer(serializers.Serializer):
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(help_text="Tenure in days/weeks/months/years depending on the schedule.")
    tenure_type = serializers.ChoiceField(choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ])
    repayment_schedule = serializers.ChoiceField(choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time'),
    ])
    repayment_mode = serializers.ChoiceField(choices=[
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically'),
    ])
    interest_basis = serializers.ChoiceField(choices=[
        ('365', '365 Days Basis'),
        ('other', 'Other Basis'),
    ])
    loan_calculation_method = serializers.ChoiceField(choices=[
        ('reducing_balance', 'Reducing Balance Method'),
        ('flat_rate', 'Flat Rate Method'),
        ('constant_repayment', 'Constant Repayment (Amortization)'),
        ('simple_interest', 'Simple Interest'),
        ('compound_interest', 'Compound Interest'),
        ('graduated_repayment', 'Graduated Repayment'),
        ('balloon_payment', 'Balloon Payment'),
        ('bullet_repayment', 'Bullet Repayment'),
        ('interest_first', 'Interest-Only Loans'),
    ])
    repayment_start_date = serializers.DateField()

    def calculate_repayment_schedule(self, validated_data):
        loan_amount = validated_data['loan_amount']
        interest_rate = validated_data['interest_rate']
        tenure = validated_data['tenure']
        tenure_type = validated_data['tenure_type']
        repayment_schedule = validated_data['repayment_schedule']
        repayment_mode = validated_data['repayment_mode']
        interest_basis = validated_data['interest_basis']
        loan_calculation_method = validated_data['loan_calculation_method']
        repayment_start_date = validated_data['repayment_start_date']

        getcontext().prec = 10  # Set precision for decimal operations

        # Determine the number of periods based on the repayment schedule
        if repayment_schedule == 'daily':
            periods = tenure if tenure_type == 'days' else tenure * 365 // {'weeks': 7, 'months': 30, 'years': 365}[
                tenure_type]
            interval = timedelta(days=1)
        elif repayment_schedule == 'weekly':
            periods = tenure if tenure_type == 'weeks' else tenure * 52 // {'days': 1 / 7, 'months': 4, 'years': 52}[
                tenure_type]
            interval = timedelta(weeks=1)
        elif repayment_schedule == 'monthly':
            periods = tenure if tenure_type == 'months' else tenure * 12 // {'days': 1 / 30, 'weeks': 4, 'years': 12}[
                tenure_type]
            interval = timedelta(days=30)  # Approximation for a month
        elif repayment_schedule == 'quarterly':
            periods = tenure * 4 // {'months': 3, 'years': 4}[tenure_type]
            interval = timedelta(days=90)
        elif repayment_schedule == 'halfyearly':
            periods = tenure * 2 // {'months': 6, 'years': 2}[tenure_type]
            interval = timedelta(days=182)
        elif repayment_schedule == 'annually':
            periods = tenure if tenure_type == 'years' else tenure * 1 // \
                                                            {'days': 1 / 365, 'weeks': 1 / 52, 'months': 1 / 12}[
                                                                tenure_type]
            interval = timedelta(days=365)
        else:  # one_time
            periods = 1
            interval = None  # No interval as it's a one-time payment

        # Adjust interest rate based on the interest basis (365 or other)
        if interest_basis == '365':
            period_interest_rate = interest_rate / Decimal(100) / Decimal(365 / periods)
        else:
            # Placeholder for other basis
            period_interest_rate = interest_rate / Decimal(100) / Decimal(365 / periods)

        # Initialize totals
        total_principal = Decimal(0)
        total_interest = Decimal(0)

        # Initialize repayment plan and remaining principal
        repayment_plan = []
        remaining_principal = loan_amount

        # Implement loan calculation methods
        if loan_calculation_method == 'reducing_balance':
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = loan_amount / periods
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'flat_rate':
            fixed_interest = loan_amount * interest_rate / Decimal(100) * tenure / Decimal(12)
            monthly_payment = (loan_amount + fixed_interest) / periods
            for period in range(1, periods + 1):
                interest_payment = fixed_interest / periods
                principal_payment = loan_amount / periods

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'constant_repayment':
            monthly_payment = (loan_amount * period_interest_rate) / (1 - (1 + period_interest_rate) ** -periods)
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = monthly_payment - interest_payment
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'simple_interest':
            interest_payment = loan_amount * interest_rate / Decimal(100) * tenure / Decimal(12)
            for period in range(1, periods + 1):
                principal_payment = loan_amount / periods

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(
                    self.build_repayment_entry(period, principal_payment, interest_payment / periods, due_date))
                total_principal += principal_payment
                total_interest += interest_payment / periods

        elif loan_calculation_method == 'compound_interest':
            compound_factor = (1 + period_interest_rate) ** periods
            total_amount = loan_amount * compound_factor
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = total_amount / periods - interest_payment
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'graduated_repayment':
            initial_payment = loan_amount / periods
            increment_factor = Decimal(1.05)  # 5% increment per period
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = initial_payment * (increment_factor ** (period - 1))
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'balloon_payment':
            balloon_amount = loan_amount * Decimal(0.5)  # 50% as balloon payment
            monthly_payment = (loan_amount - balloon_amount) / (periods - 1)
            for period in range(1, periods):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = monthly_payment - interest_payment
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

            # Balloon payment in the last period
            repayment_plan.append(
                self.build_repayment_entry(periods, balloon_amount, remaining_principal * period_interest_rate,
                                           repayment_start_date + (interval * (periods - 1))))
            total_principal += balloon_amount
            total_interest += remaining_principal * period_interest_rate

        elif loan_calculation_method == 'bullet_repayment':
            for period in range(1, periods):
                interest_payment = remaining_principal * period_interest_rate
                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, 0, interest_payment, due_date))
                total_interest += interest_payment

            # Principal paid in the last period
            repayment_plan.append(
                self.build_repayment_entry(periods, loan_amount, remaining_principal * period_interest_rate,
                                           repayment_start_date + (interval * (periods - 1))))
            total_principal += loan_amount
            total_interest += remaining_principal * period_interest_rate

        elif loan_calculation_method == 'interest_first':
            for period in range(1, periods):
                interest_payment = remaining_principal * period_interest_rate
                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self.build_repayment_entry(period, 0, interest_payment, due_date))
                total_interest += interest_payment

            # Principal paid in the last period
            repayment_plan.append(
                self.build_repayment_entry(periods, loan_amount, 0, repayment_start_date + (interval * (periods - 1))))
            total_principal += loan_amount

        return {
            'repayment_plan': repayment_plan,
            'total_principal': round(total_principal, 2),
            'total_interest': round(total_interest, 2),
            'total_amount_to_repay': round(total_principal + total_interest, 2)
        }

    def build_repayment_entry(self, period, principal, interest, due_date):
        return {
            'period': period,
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'installment': round(principal + interest, 2),
            'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
        }


class LoanApprovalSerializer(serializers.ModelSerializer):
    funeral_period_count = serializers.IntegerField(required=True)
    funeral_period_type = serializers.ChoiceField(choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], required=True)
    application_expiry_date = serializers.DateField(required=True)
    repayment_start_date = serializers.DateField(read_only=True)

    class Meta:
        model = LoanApplication
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'repayment_start_date']

    def update(self, instance, validated_data):
        # Update instance with new data
        instance.application_expiry_date = validated_data.get('application_expiry_date',
                                                              instance.application_expiry_date)
        instance.funeral_period_count = validated_data.get('funeral_period_count', instance.funeral_period_count)
        instance.funeral_period_type = validated_data.get('funeral_period_type', instance.funeral_period_type)

        # Calculate the repayment start date
        instance.calculate_repayment_start_date()

        # Approve the loan application and generate the repayment schedule
        instance.approve_application()

        # Save the instance
        instance.save()

        return instance


class LoanModificationSerializer(serializers.ModelSerializer):
    current_principal_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    principal_increase_decrease = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = LoanModification
        fields = [
            'loan_application', 'current_principal_amount', 'principal_increase_decrease',
            'new_interest_rate', 'new_term_years', 'new_frequency',
            'new_repayment_option', 'new_interest_basis', 'status', 'modification_date', 'modified_by'
        ]
        read_only_fields = ['modification_date', 'current_principal_amount']

    def validate(self, data):
        if data['loan_application'].status != 'approved':
            raise serializers.ValidationError("Loan application must be approved to modify parameters.")
        return data

    def create(self, validated_data):
        loan_application = validated_data['loan_application']
        remaining_principal = self.get_remaining_principal(loan_application)

        # Set the current principal amount
        validated_data['current_principal_amount'] = remaining_principal

        modification = LoanModification.objects.create(**validated_data)

        if modification.status == 'approved':
            modification.apply_modification()  # Apply the changes if the status is approved

        return modification

    def get_remaining_principal(self, loan_application):
        future_schedules = LoanSchedule.objects.filter(
            application=loan_application,
            due_date__gte=timezone.now()
        )
        return sum(schedule.principal_amount for schedule in future_schedules if schedule.status == 'pending')


# Past Due Processing ------

class PastDueRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastDueRecord
        fields = '__all__'


class PDActionWorkflowConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDActionWorkflowConfig
        fields = '__all__'


class PDNextActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDNextAction
        fields = '__all__'


class PenaltyAccrualSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenaltyAccrual
        fields = '__all__'


class PDCommunicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDCommunicationLog
        fields = '__all__'


class PDLegalActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDLegalAction
        fields = '__all__'


class PDPenaltiesChargesConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDPenaltiesChargesConfig
        fields = '__all__'


class LoanAccountReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAccountReceivable
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'  # Or specify the fields you want to include
