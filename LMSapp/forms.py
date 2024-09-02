from django import forms
from .models import *

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']  # List all fields you want in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)