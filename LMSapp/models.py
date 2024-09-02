import string
from datetime import timedelta
import random
from decimal import Decimal, getcontext
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('loan', 'Loan Account'),
        ('disbursement', 'Disbursement Account'),
        ('repayment', 'Repayment Account'),
        ('internal_funding', 'Funding Account'),
        ('internal', 'Internal Account'),
        ('internal_suspense', 'Internal Suspense Account'),
        ('interest_accrual', 'Interest Accrual Account'),
        ('penalty_accrual', 'Penalty Accrual Account'),
        ('personal_customer', 'Customer Personal Account'),
        ('current_customer', 'Customer Current Account'),
        ('business_customer', 'Customer Business Account'),
    ]

    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    general_ledger_no = models.IntegerField()
    account_number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.account_name} - {self.get_account_type_display()}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super(Account, self).save(*args, **kwargs)

    @staticmethod
    def generate_account_number():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


class LoanAccount(models.Model):
    loan_application = models.OneToOneField('LoanApplication', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    accrued_interest = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    accrued_penalty = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    advance_payment_balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))  # New Field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    transaction_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class DisbursementAccount(models.Model):
    loan_account = models.OneToOneField(LoanAccount, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RepaymentAccount(models.Model):
    loan_account = models.OneToOneField(LoanAccount, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DueRegister(models.Model):
    DUE_TYPES = [
        ('principal', 'Principal'),
        ('interest', 'Interest'),
        ('penalty', 'Penalty'),
    ]
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    due_type = models.CharField(max_length=10, choices=DUE_TYPES)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class PaidItem(models.Model):
    due_register = models.OneToOneField(DueRegister, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    paid_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class RepaymentPriority(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50)
    priority_order = models.JSONField()  # Example: {"1": "interest", "2": "penalty", "3": "principal"}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class LoanApplication(models.Model):
    application_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50)
    loan_amount = models.DecimalField(max_digits=16, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    term_count = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    term_metric = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], default='months')
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time')
    ], default='monthly')
    repayment_option = models.CharField(max_length=20, choices=[
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically')
    ], default='both')
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
                              default='submitted')
    repayment_start_date = models.DateField(null=True, blank=True)
    funeral_period_count = models.IntegerField(null=True, blank=True)
    funeral_period_type = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], null=True, blank=True)
    application_expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_repayment_start_date(self):
        if not self.application_expiry_date:
            raise ValueError("Application expiry date must be set.")

        if self.funeral_period_count is None or self.funeral_period_type is None:
            raise ValueError("Funeral period count and type must be set.")

        # Calculate funeral period in days
        if self.funeral_period_type == 'days':
            funeral_period_in_days = timedelta(days=self.funeral_period_count)
        elif self.funeral_period_type == 'weeks':
            funeral_period_in_days = timedelta(weeks=self.funeral_period_count)
        elif self.funeral_period_type == 'months':
            funeral_period_in_days = timedelta(days=self.funeral_period_count * 30)  # Approximation for months
        elif self.funeral_period_type == 'years':
            funeral_period_in_days = timedelta(days=self.funeral_period_count * 365)  # Approximation for years

        # Calculate the repayment start date
        self.repayment_start_date = self.application_expiry_date + funeral_period_in_days + timedelta(days=1)

    def calculate_tenure(self):
        if self.term_metric == 'days':
            tenure = self.term_count / Decimal(30)  # Convert days to months (approximate)
        elif self.term_metric == 'weeks':
            tenure = self.term_count / Decimal(4)  # Convert weeks to months (approximate)
        elif self.term_metric == 'months':
            tenure = self.term_count  # Already in months
        elif self.term_metric == 'years':
            tenure = self.term_count * Decimal(12)  # Convert years to months
        else:
            raise ValueError("Invalid term_metric value.")
        return int(tenure)

    def approve_application(self):
        if self.status != 'approved':
            # Calculate repayment start date
            self.calculate_repayment_start_date()

            self.status = 'approved'
            self.save()
            self.generate_repayment_schedule()

    def generate_repayment_schedule(self):
        tenure_in_months = self.calculate_tenure()

        if not self.repayment_start_date:
            raise ValueError("Repayment start date must be set before generating the repayment schedule.")

        # Instantiate the ReusableLoanCalculator
        calculator = ReusableLoanCalculator(
            loan_amount=self.loan_amount,
            interest_rate=self.interest_rate,
            tenure=tenure_in_months,
            tenure_type='months',  # Always using 'months' as default here
            repayment_schedule=self.frequency,
            repayment_mode=self.repayment_option,
            interest_basis='365',  # Assuming 365 days interest basis
            loan_calculation_method='constant_repayment',  # You can map this to a proper method
            repayment_start_date=self.repayment_start_date  # Use the calculated repayment start date
        )

        # Calculate the repayment schedule
        repayment_plan = calculator.calculate_repayment_schedule()

        # Save each schedule entry in the LoanSchedule model
        for entry in repayment_plan['repayment_plan']:
            LoanSchedule.objects.create(
                application=self,
                installment_number=entry['period'],
                due_date=entry['due_date'],
                principal_amount=entry['principal'],
                interest_amount=entry['interest'],
                total_amount=entry['installment'],
                status='pending'
            )


class LoanSchedule(models.Model):
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='schedules')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=16, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=16, decimal_places=2)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        ordering = ['due_date']


class DocumentType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=255)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    loan_application = models.ForeignKey('LoanApplication', on_delete=models.CASCADE, null=True, blank=True)
    global_access = models.BooleanField(default=False)  # Global access if True
    user_access = models.ManyToManyField('auth.User', related_name='document_access',
                                         blank=True)  # User-specific access
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class IdentityVerification(models.Model):
    verification_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('verified', 'Verified'),
        ('failed', 'Failed')
    ], default='failed')
    verification_details = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)


class CreditHistory(models.Model):
    credit_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    credit_score = models.IntegerField()
    credit_report = models.TextField()  # or FileField for file upload
    checked_at = models.DateTimeField(auto_now_add=True)


class FraudCheck(models.Model):
    fraud_check_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    fraud_score = models.IntegerField()
    alerts = models.TextField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)


class EmploymentVerification(models.Model):
    employment_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    employer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('verified', 'Verified'),
        ('failed', 'Failed')
    ], default='failed')
    verified_at = models.DateTimeField(auto_now_add=True)


class LoanOfficer(models.Model):
    officer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class LoanOfficerReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    officer = models.ForeignKey(LoanOfficer, on_delete=models.CASCADE)
    decision = models.CharField(max_length=20, choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('request_more_info', 'Request More Info')
    ], default='approved')
    comments = models.TextField(null=True, blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)


class LoanAgreement(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    document_path = models.FileField(upload_to='agreements/')
    generated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('generated', 'Generated'),
        ('signed', 'Signed'),
        ('pending', 'Pending')
    ], default='pending')


class Signature(models.Model):
    signature_id = models.AutoField(primary_key=True)
    agreement = models.ForeignKey(LoanAgreement, on_delete=models.CASCADE)
    signature_data = models.TextField()  # or FileField for signature file
    signed_at = models.DateTimeField(auto_now_add=True)


class Disbursement(models.Model):
    disbursement_id = models.AutoField(primary_key=True)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    bank_account = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    disbursed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')


class RepaymentSchedule(models.Model):
    loan_application = models.ForeignKey('LoanApplication', on_delete=models.CASCADE)
    installment_number = models.IntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=16, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=16, decimal_places=2)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2)
    penalty_amount = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))  # New Field
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE)
    reminder_date = models.DateTimeField()
    reminder_channel = models.CharField(max_length=20, choices=[
        ('SMS', 'SMS'),
        ('Email', 'Email')
    ])
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('pending', 'Pending')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=50, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card')
    ])
    status = models.CharField(max_length=20, choices=[
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='completed')


class LatePayment(models.Model):
    late_payment_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE)
    days_late = models.IntegerField()
    penalty_amount = models.DecimalField(max_digits=16, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved')
    ], default='pending')


class BalanceAdjustment(models.Model):
    adjustment_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=20, choices=[
        ('prepayment', 'Prepayment'),
        ('penalty', 'Penalty')
    ])
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    adjusted_at = models.DateTimeField(auto_now_add=True)
    new_balance = models.DecimalField(max_digits=16, decimal_places=2)


class LoanMonitoring(models.Model):
    monitoring_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(RepaymentSchedule, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50, choices=[
        ('delinquency', 'Delinquency'),
        ('payment_risk', 'Payment Risk')
    ])
    alert_date = models.DateTimeField(auto_now_add=True)
    action_taken = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved')
    ], default='pending')


class LoanRestructuring(models.Model):
    restructuring_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    requested_terms = models.TextField()  # or JSONField if you want to store structured data
    approved_terms = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='requested')
    created_at = models.DateTimeField(auto_now_add=True)


class Collection(models.Model):
    collection_id = models.AutoField(primary_key=True)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=[
        ('reminder', 'Reminder'),
        ('legal_notice', 'Legal Notice'),
        ('third_party_agency', 'Third Party Agency')
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Settlement(models.Model):
    loan_application = models.ForeignKey('LoanApplication', on_delete=models.CASCADE)
    settlement_amount = models.DecimalField(max_digits=16, decimal_places=2)
    settlement_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ], default='pending')
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Settlement for Loan {self.loan_application_id} - {self.status}"


class LoanReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_type = models.CharField(max_length=50, choices=[
        ('performance', 'Performance'),
        ('delinquency', 'Delinquency')
    ])
    generated_at = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField()  # or TextField if storing as plain text or file path
    created_at = models.DateTimeField(auto_now_add=True)


class CustomerProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    credit_score = models.IntegerField()
    loan_history = models.JSONField()  # or TextField for unstructured data
    updated_at = models.DateTimeField(auto_now_add=True)


class CreditAssessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    credit_score = models.IntegerField()
    risk_rating = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    assessment_date = models.DateTimeField(auto_now_add=True)
    loan_offer_recommendations = models.JSONField()  # or TextField if storing as plain text


class CustomerCommunication(models.Model):
    communication_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message_content = models.TextField()
    communication_type = models.CharField(max_length=50, choices=[
        ('status_update', 'Status Update'),
        ('promotion', 'Promotion')
    ])
    sent_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ], default='sent')


class RetentionOffer(models.Model):
    offer_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    offer_details = models.JSONField()  # or TextField for unstructured data
    sent_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')


class RetentionMetric(models.Model):
    metric_id = models.AutoField(primary_key=True)
    metric_type = models.CharField(max_length=50, choices=[
        ('churn_rate', 'Churn Rate'),
        ('loyalty_participation', 'Loyalty Participation')
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True)

class Ledger(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    debit_account = models.ForeignKey(Account, related_name='debit_entries', on_delete=models.CASCADE)
    credit_account = models.ForeignKey(Account, related_name='credit_entries', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    entry_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ledger Entry: {self.debit_account.name} -> {self.credit_account.name} : {self.amount}"


class LoanModification(models.Model):
    modification_id = models.AutoField(primary_key=True)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='modifications')
    current_principal_amount = models.DecimalField(max_digits=16, decimal_places=2)  # Displayed to the user
    principal_increase_decrease = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_term_count = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_term_metric = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], null=True, blank=True)
    new_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time')
    ], null=True, blank=True)
    new_repayment_option = models.CharField(max_length=20, choices=[
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically')
    ], null=True, blank=True)
    new_interest_basis = models.CharField(max_length=10, choices=[
        ('365', '365 Days Basis'),
        ('other', 'Other Basis'),
    ], null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='submitted')
    modification_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100)

    def apply_modification(self):
        if self.status != 'approved':
            raise ValueError("Modification must be approved to apply changes.")

        # Create a history record before modifying the loan application
        self.create_loan_application_history()

        loan_application = self.loan_application

        # Adjust the loan amount based on principal increase or decrease
        if self.principal_increase_decrease is not None:
            remaining_principal = self.get_remaining_principal()
            loan_application.loan_amount = remaining_principal + self.principal_increase_decrease

        # Update other loan parameters if provided
        if self.new_interest_rate:
            loan_application.interest_rate = self.new_interest_rate
        if self.new_term_count and self.new_term_metric:
            loan_application.term_count = self.new_term_count
            loan_application.term_metric = self.new_term_metric
        if self.new_frequency:
            loan_application.frequency = self.new_frequency
        if self.new_repayment_option:
            loan_application.repayment_option = self.new_repayment_option
        if self.new_interest_basis:
            loan_application.interest_basis = self.new_interest_basis

        loan_application.save()

        # Recalculate future schedules
        self.recalculate_future_schedules()

    def create_loan_application_history(self):
        LoanApplicationHistory.objects.create(
            loan_application=self.loan_application,
            customer=self.loan_application.customer,
            loan_type=self.loan_application.loan_type,
            loan_amount=self.loan_application.loan_amount,
            interest_rate=self.loan_application.interest_rate,
            term_count=self.loan_application.term_count,
            term_metric=self.loan_application.term_metric,
            frequency=self.loan_application.frequency,
            repayment_option=self.loan_application.repayment_option,
            interest_basis=self.loan_application.interest_basis,
            status=self.loan_application.status,
            created_at=self.loan_application.created_at,
            updated_at=self.loan_application.updated_at
        )

    def get_remaining_principal(self):
        # Calculate the remaining principal from future schedules
        future_schedules = LoanSchedule.objects.filter(
            application=self.loan_application,
            due_date__gte=models.DateField.auto_now_add
        ).order_by('due_date')

        return sum(schedule.principal_amount for schedule in future_schedules if schedule.status == 'pending')

    def recalculate_future_schedules(self):
        loan_application = self.loan_application
        today = models.DateField.auto_now_add

        # Fetch and delete all future schedules
        future_schedules = LoanSchedule.objects.filter(
            application=loan_application,
            due_date__gte=today
        ).order_by('due_date')

        future_schedules.delete()

        # Instantiate and use the ReusableLoanCalculator to calculate the new schedule
        calculator = ReusableLoanCalculator(
            loan_amount=loan_application.loan_amount,
            interest_rate=loan_application.interest_rate,
            tenure=loan_application.calculate_tenure(),
            # Recalculate tenure using the updated term_count and term_metric
            tenure_type='months',  # Assuming tenure type is always in months for now
            repayment_schedule=loan_application.frequency,
            repayment_mode=loan_application.repayment_option,
            interest_basis=loan_application.interest_basis or '365',  # Use the modified interest_basis if provided
            loan_calculation_method='constant_repayment',  # You can map this to a proper method
            repayment_start_date=today  # Continue from today
        )

        repayment_plan = calculator.calculate_repayment_schedule()

        for entry in repayment_plan['repayment_plan']:
            LoanSchedule.objects.create(
                application=loan_application,
                installment_number=entry['period'],
                due_date=entry['due_date'],
                principal_amount=entry['principal'],
                interest_amount=entry['interest'],
                total_amount=entry['installment'],
                status='pending'
            )


class LoanApplicationHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    loan_application = models.ForeignKey('LoanApplication', on_delete=models.CASCADE, related_name='history')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50)
    loan_amount = models.DecimalField(max_digits=16, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    term_count = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    term_metric = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], default='months')
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time')
    ], default='monthly')
    repayment_option = models.CharField(max_length=20, choices=[
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically')
    ], default='both')
    interest_basis = models.CharField(max_length=10, choices=[
        ('365', '365 Days Basis'),
        ('other', 'Other Basis'),
    ], default='365')
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
                              default='submitted')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    modification_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-modification_date']


class LoanInterestAccrual(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    accrual_date = models.DateField()
    interest_amount = models.DecimalField(max_digits=16, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class LoanPenaltiesAccrual(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    penalty_date = models.DateField()
    penalty_amount = models.DecimalField(max_digits=16, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class LoanAccountEntry(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=20)  # e.g., 'disbursement', 'interest', 'penalty', 'repayment'
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    entry_date = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class LoanRepaymentTry(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    try_count = models.IntegerField()
    status = models.CharField(max_length=20)  # e.g., 'failed', 'successful'
    response_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RepaymentEODRetry(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    repayment_schedule_id = models.IntegerField()
    retry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class FailedLoanRepayments(models.Model):
    loan_account = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    schedule_id = models.IntegerField()
    try_ids = models.JSONField()  # Stores all retry IDs
    created_at = models.DateTimeField(auto_now_add=True)


class ReusableLoanCalculator:
    def __init__(self, loan_amount, interest_rate, tenure, tenure_type, repayment_schedule, repayment_mode,
                 interest_basis, loan_calculation_method, repayment_start_date):
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.tenure = tenure
        self.tenure_type = tenure_type
        self.repayment_schedule = repayment_schedule
        self.repayment_mode = repayment_mode
        self.interest_basis = interest_basis
        self.loan_calculation_method = loan_calculation_method
        self.repayment_start_date = repayment_start_date

        getcontext().prec = 10  # Set precision for decimal operations

    def calculate_repayment_schedule(self):
        loan_amount = self.loan_amount
        interest_rate = self.interest_rate
        tenure = self.tenure
        tenure_type = self.tenure_type
        repayment_schedule = self.repayment_schedule
        repayment_mode = self.repayment_mode
        interest_basis = self.interest_basis
        loan_calculation_method = self.loan_calculation_method
        repayment_start_date = self.repayment_start_date

        # Determine the number of periods based on the repayment schedule
        periods, interval = self._determine_periods_and_interval(tenure, tenure_type, repayment_schedule)

        # Adjust interest rate based on the interest basis (365 or other)
        period_interest_rate = self._adjust_interest_rate(interest_rate, interest_basis, periods)

        # Initialize totals
        total_principal = Decimal(0)
        total_interest = Decimal(0)

        # Initialize repayment plan and remaining principal
        repayment_plan = []
        remaining_principal = loan_amount

        # Implement loan calculation methods
        repayment_plan, total_principal, total_interest = self._calculate_loan_repayments(
            periods, interval, interest_rate, remaining_principal, period_interest_rate, repayment_start_date,
            loan_amount, total_principal, total_interest, loan_calculation_method
        )

        return {
            'repayment_plan': repayment_plan,
            'total_principal': round(total_principal, 2),
            'total_interest': round(total_interest, 2),
            'total_amount_to_repay': round(total_principal + total_interest, 2)
        }

    def _determine_periods_and_interval(self, tenure, tenure_type, repayment_schedule):
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

        return periods, interval

    def _adjust_interest_rate(self, interest_rate, interest_basis, periods):
        if interest_basis == '365':
            return interest_rate / Decimal(100) / Decimal(365 / periods)
        else:
            return interest_rate / Decimal(100) / Decimal(365 / periods)  # Placeholder for other basis

    def _calculate_loan_repayments(self, periods, interval, interest_rate, remaining_principal, period_interest_rate,
                                   repayment_start_date, loan_amount, total_principal, total_interest,
                                   loan_calculation_method):
        repayment_plan = []

        if loan_calculation_method == 'reducing_balance':
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = loan_amount / periods
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'flat_rate':
            fixed_interest = loan_amount * interest_rate / Decimal(100) * periods / Decimal(12)
            monthly_payment = (loan_amount + fixed_interest) / periods
            for period in range(1, periods + 1):
                interest_payment = fixed_interest / periods
                principal_payment = loan_amount / periods

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'constant_repayment':
            monthly_payment = (loan_amount * period_interest_rate) / (1 - (1 + period_interest_rate) ** -periods)
            for period in range(1, periods + 1):
                interest_payment = remaining_principal * period_interest_rate
                principal_payment = monthly_payment - interest_payment
                remaining_principal -= principal_payment

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

        elif loan_calculation_method == 'simple_interest':
            interest_payment = loan_amount * interest_rate / Decimal(100) * periods / Decimal(12)
            for period in range(1, periods + 1):
                principal_payment = loan_amount / periods

                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment / periods, due_date))
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
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
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
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
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
                repayment_plan.append(
                    self._build_repayment_entry(period, principal_payment, interest_payment, due_date))
                total_principal += principal_payment
                total_interest += interest_payment

            # Balloon payment in the last period
            repayment_plan.append(
                self._build_repayment_entry(periods, balloon_amount, remaining_principal * period_interest_rate,
                                            repayment_start_date + (interval * (periods - 1))))
            total_principal += balloon_amount
            total_interest += remaining_principal * period_interest_rate

        elif loan_calculation_method == 'bullet_repayment':
            for period in range(1, periods):
                interest_payment = remaining_principal * period_interest_rate
                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self._build_repayment_entry(period, 0, interest_payment, due_date))
                total_interest += interest_payment

            # Principal paid in the last period
            repayment_plan.append(
                self._build_repayment_entry(periods, loan_amount, remaining_principal * period_interest_rate,
                                            repayment_start_date + (interval * (periods - 1))))
            total_principal += loan_amount
            total_interest += remaining_principal * period_interest_rate

        elif loan_calculation_method == 'interest_first':
            for period in range(1, periods):
                interest_payment = remaining_principal * period_interest_rate
                due_date = repayment_start_date + (interval * (period - 1)) if interval else repayment_start_date
                repayment_plan.append(self._build_repayment_entry(period, 0, interest_payment, due_date))
                total_interest += interest_payment

            # Principal paid in the last period
            repayment_plan.append(
                self._build_repayment_entry(periods, loan_amount, 0, repayment_start_date + (interval * (periods - 1))))
            total_principal += loan_amount

        return repayment_plan, total_principal, total_interest

    def _build_repayment_entry(self, period, principal, interest, due_date):
        return {
            'period': period,
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'installment': round(principal + interest, 2),
            'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
        }


# past due process ------------

class PastDueRecord(models.Model):
    pd_record_id = models.AutoField(primary_key=True)
    loan_account_id = models.IntegerField()
    repayment_schedule_id = models.IntegerField()
    overdue_amount = models.DecimalField(max_digits=12, decimal_places=2)
    overdue_date = models.DateField()
    days_overdue = models.IntegerField()
    status = models.CharField(max_length=50)  # Active, Resolved, Written-off
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Past Due Record {self.pd_record_id} for Loan Account {self.loan_account_id}"


class PDActionWorkflowConfig(models.Model):
    # Define the choices for the current PD status
    PD_STATUS_CHOICES = [
        ('0-30 Days', '0-30 Days'),
        ('31-60 Days', '31-60 Days'),
        ('61-90 Days', '61-90 Days'),
        ('Above 90 Days', 'Above 90 Days'),
    ]

    workflow_id = models.AutoField(primary_key=True)
    current_pd_status = models.CharField(max_length=50, choices=PD_STATUS_CHOICES)
    next_action_type = models.CharField(max_length=100)
    action_timeline_days = models.IntegerField()
    next_pd_status = models.CharField(max_length=50, choices=PD_STATUS_CHOICES)
    additional_details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workflow {self.workflow_id} for Status {self.current_pd_status}"


class PDNextAction(models.Model):
    next_action_id = models.AutoField(primary_key=True)
    pd_record_id = models.ForeignKey(PastDueRecord, on_delete=models.CASCADE)
    next_action_date = models.DateField()
    next_action_type = models.CharField(max_length=100)
    action_status = models.CharField(max_length=50, default="Pending")
    current_pd_status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Next Action {self.next_action_id} for PD Record {self.pd_record_id}"


class PenaltyAccrual(models.Model):
    penalty_id = models.AutoField(primary_key=True)
    pd_record_id = models.ForeignKey(PastDueRecord, on_delete=models.CASCADE)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2)
    penalty_date = models.DateField()
    penalty_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)  # Applied, Waived, Paid
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Penalty {self.penalty_id} for PD Record {self.pd_record_id}"


class PDCommunicationLog(models.Model):
    communication_id = models.AutoField(primary_key=True)
    pd_record_id = models.ForeignKey(PastDueRecord, on_delete=models.CASCADE)
    communication_date = models.DateTimeField()
    communication_type = models.CharField(max_length=100)  # Reminder, Warning, Final Notice
    mode_of_communication = models.CharField(max_length=50)  # Email, SMS, Direct Call
    message_content = models.TextField()
    status = models.CharField(max_length=50)  # Sent, Acknowledged, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Communication {self.communication_id} for PD Record {self.pd_record_id}"


class PDLegalAction(models.Model):
    legal_action_id = models.AutoField(primary_key=True)
    pd_record_id = models.ForeignKey(PastDueRecord, on_delete=models.CASCADE)
    action_id = models.CharField(max_length=100)  # Legal Notice ID, Court Case Number
    legal_action_date = models.DateField()
    action_type = models.CharField(max_length=100)
    outcome = models.CharField(max_length=100, null=True, blank=True)  # Pending, Resolved, In Progress
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Legal Action {self.legal_action_id} for PD Record {self.pd_record_id}"


class PDPenaltiesChargesConfig(models.Model):
    config_id = models.AutoField(primary_key=True)
    penalty_type = models.CharField(max_length=100)
    charge_amount = models.DecimalField(max_digits=12, decimal_places=2)
    charge_frequency = models.CharField(max_length=50)  # Daily, Monthly
    charge_trigger = models.CharField(max_length=100)  # X Days Overdue
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Penalty Config {self.config_id} for {self.penalty_type}"


class LoanAccountReceivable(models.Model):
    receivable_id = models.AutoField(primary_key=True)
    loan_account_id = models.IntegerField()
    pd_record_id = models.ForeignKey(PastDueRecord, on_delete=models.CASCADE)
    amount_type = models.CharField(max_length=100)  # Penalty, Interest Accrual
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=50)  # Due, Paid, Overdue
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receivable {self.receivable_id} for Loan Account {self.loan_account_id}"


class Loan(models.Model):
    borrower_name = models.CharField(max_length=255)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.borrower_name} - {self.loan_amount}'