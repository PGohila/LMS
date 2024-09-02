from django.shortcuts import get_object_or_404
from .models import *
from .forms import *  # Assuming you have a form for Company
from .serializers import *
from .scripts import *

# manageing CRUD operations for company
def create_company(name):
    try:
        companys = Company.objects.create(
            name = name
        )
        return success_response("Successfully Saved Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))

# Read
def company_list():
    try:
        companies = Company.objects.all()
        serializer = CompanySerializer(companies,many = True).data
        return success_response(serializer)
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))
    
# Update
def update_company(company_id,name):
    try:
        company = get_object_or_404(Company, id=company_id)
        company.name = name
        return success_response("Successfully update Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))

# Delete
def delete_company(company_id):
    try:
        company = get_object_or_404(Company, id=company_id)
        company.delete()
        return success_response("Successfully delete Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))


#============= custemer management ============================
# Manages customer CRUD operations.
def create_custemer(name,email,phone_number,address,date_of_birth):
    try:
        Customers = Customer.objects.create(
            name = name,
            email = email,
            phone_number = phone_number,
            address = address,
            date_of_birth = date_of_birth
        )
        return success_response("Successfully Saved Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))

# Read
def company_list():
    try:
        companies = Company.objects.all()
        serializer = CompanySerializer(companies,many = True).data
        return success_response(serializer)
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))
    
# Update
def update_company(company_id,name):
    try:
        company = get_object_or_404(Company, id=company_id)
        company.name = name
        return success_response("Successfully update Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))

# Delete
def delete_company(company_id):
    try:
        company = get_object_or_404(Company, id=company_id)
        company.delete()
        return success_response("Successfully delete Custemer")
    except Exception as error:
        print(f"Error Occured {str(error)}")
        return fail_response(str(error))