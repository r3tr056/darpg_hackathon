from django import forms
from .models import GrievanceReport

class GrievanceReportForm(forms.Form):
    class Meta:
        model = GrievanceReport
        fields = ['title', 'description', 'category']