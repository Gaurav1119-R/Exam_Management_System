"""
Forms for project report management.
"""
from django import forms
from .models import ProjectReport


class ProjectReportForm(forms.ModelForm):
    """Form for uploading project reports."""
    
    class Meta:
        model = ProjectReport
        fields = ['title', 'description', 'file', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StudentProjectReportForm(forms.ModelForm):
    """Form for students to submit project reports."""
    
    class Meta:
        model = ProjectReport
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProjectReportGradingForm(forms.ModelForm):
    """Form for admin to grade project reports."""
    
    class Meta:
        model = ProjectReport
        fields = ['marks_obtained', 'feedback', 'status']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
