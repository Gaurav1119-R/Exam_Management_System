"""
Forms for attendance management.
"""
from django import forms
from .models import Attendance


class AttendanceForm(forms.ModelForm):
    """Form for marking attendance."""
    
    class Meta:
        model = Attendance
        fields = ['attended', 'check_in_time', 'check_out_time', 'notes']
        widgets = {
            'check_in_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking."""
    exam_schedule = forms.ModelChoiceField(
        queryset=None,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        from apps.exams.models import ExamSchedule
        super().__init__(*args, **kwargs)
        self.fields['exam_schedule'].queryset = ExamSchedule.objects.filter(
            status__in=['ongoing', 'completed']
        )
