from datetime import timedelta, date
from .models import LoanSchedule, LoanApplicationHistory
from .serializers import LoanCalculatorSerializer


def calculate_repayment_start_date(loan_application):
    if not loan_application.application_expiry_date:
        raise ValueError("Application expiry date must be set.")

    if loan_application.funeral_period_count is None or loan_application.funeral_period_type is None:
        raise ValueError("Funeral period count and type must be set.")

    # Calculate funeral period in days
    if loan_application.funeral_period_type == 'days':
        funeral_period_in_days = timedelta(days=loan_application.funeral_period_count)
    elif loan_application.funeral_period_type == 'weeks':
        funeral_period_in_days = timedelta(weeks=loan_application.funeral_period_count)
    elif loan_application.funeral_period_type == 'months':
        funeral_period_in_days = timedelta(days=loan_application.funeral_period_count * 30)  # Approximation for months
    elif loan_application.funeral_period_type == 'years':
        funeral_period_in_days = timedelta(days=loan_application.funeral_period_count * 365)  # Approximation for years

    # Calculate the repayment start date
    return loan_application.application_expiry_date + funeral_period_in_days + timedelta(days=1)


def generate_repayment_schedule(loan_application):
    if not loan_application.repayment_start_date:
        raise ValueError("Repayment start date must be set before generating the repayment schedule.")

    # Prepare data for the serializer
    data = {
        'loan_amount': loan_application.loan_amount,
        'interest_rate': loan_application.interest_rate,
        'tenure': int(loan_application.term_years * 12),  # Assuming term_years is in years
        'tenure_type': 'months',  # Assuming tenure type is always in months for now
        'repayment_schedule': loan_application.frequency,
        'repayment_mode': loan_application.repayment_option,
        'interest_basis': '365',  # Assuming 365 days interest basis
        'loan_calculation_method': 'constant_repayment',  # You can map this to a proper method
        'repayment_start_date': loan_application.repayment_start_date,  # Use the calculated repayment start date
    }

    # Instantiate the serializer and calculate the schedule
    serializer = LoanCalculatorSerializer(data=data)
    if serializer.is_valid():
        repayment_plan = serializer.calculate_repayment_schedule(serializer.validated_data)
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


def apply_loan_modification(loan_modification):
    if loan_modification.status != 'approved':
        raise ValueError("Modification must be approved to apply changes.")

    # Create a history record before modifying the loan application
    LoanApplicationHistory.objects.create(
        loan_application=loan_modification.loan_application,
        customer=loan_modification.loan_application.customer,
        loan_type=loan_modification.loan_application.loan_type,
        loan_amount=loan_modification.loan_application.loan_amount,
        interest_rate=loan_modification.loan_application.interest_rate,
        term_years=loan_modification.loan_application.term_years,
        frequency=loan_modification.loan_application.frequency,
        repayment_option=loan_modification.loan_application.repayment_option,
        interest_basis=loan_modification.loan_application.interest_basis,
        status=loan_modification.loan_application.status,
        created_at=loan_modification.loan_application.created_at,
        updated_at=loan_modification.loan_application.updated_at
    )

    loan_application = loan_modification.loan_application

    # Adjust the loan amount based on principal increase or decrease
    if loan_modification.principal_increase_decrease is not None:
        remaining_principal = get_remaining_principal(loan_modification)
        loan_application.loan_amount = remaining_principal + loan_modification.principal_increase_decrease

    # Update other loan parameters if provided
    if loan_modification.new_interest_rate:
        loan_application.interest_rate = loan_modification.new_interest_rate
    if loan_modification.new_term_years:
        loan_application.term_years = loan_modification.new_term_years
    if loan_modification.new_frequency:
        loan_application.frequency = loan_modification.new_frequency
    if loan_modification.new_repayment_option:
        loan_application.repayment_option = loan_modification.new_repayment_option
    if loan_modification.new_interest_basis:
        loan_application.interest_basis = loan_modification.new_interest_basis

    loan_application.save()

    # Recalculate future schedules
    recalculate_future_schedules(loan_modification)


def get_remaining_principal(loan_modification):
    future_schedules = LoanSchedule.objects.filter(
        application=loan_modification.loan_application,
        due_date__gte=loan_modification.modification_date
    ).order_by('due_date')

    return sum(schedule.principal_amount for schedule in future_schedules if schedule.status == 'pending')


def recalculate_future_schedules(loan_modification):
    loan_application = loan_modification.loan_application
    today = loan_modification.modification_date

    # Fetch and delete all future schedules
    future_schedules = LoanSchedule.objects.filter(
        application=loan_application,
        due_date__gte=today
    ).order_by('due_date')

    future_schedules.delete()

    # Recalculate future schedules based on modified parameters
    data = {
        'loan_amount': loan_application.loan_amount,
        'interest_rate': loan_application.interest_rate,
        'tenure': int(loan_application.term_years * 12),  # Assuming term_years is in years
        'tenure_type': 'months',  # Assuming tenure type is always in months for now
        'repayment_schedule': loan_application.frequency,
        'repayment_mode': loan_application.repayment_option,
        'interest_basis': loan_application.interest_basis or '365',  # Use the modified interest_basis if provided
        'loan_calculation_method': 'constant_repayment',  # You can map this to a proper method
        'repayment_start_date': today,  # Continue from today
    }

    # Instantiate the serializer and calculate the new schedule
    serializer = LoanCalculatorSerializer(data=data)
    if serializer.is_valid():
        repayment_plan = serializer.calculate_repayment_schedule(serializer.validated_data)
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
