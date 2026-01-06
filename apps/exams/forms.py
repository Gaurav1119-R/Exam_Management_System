"""
Forms for exam management (admin) and exam taking (student).
"""
from django import forms
from django.forms import inlineformset_factory
from .models import Subject, Question, QuestionPaper, ExamSchedule
from apps.accounts.models import StudentProfile


class SubjectForm(forms.ModelForm):
    """Form for creating/updating subjects."""
    
    class Meta:
        model = Subject
        fields = ['code', 'name', 'description', 'credits']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    """Form for creating/updating questions."""
    
    class Meta:
        model = Question
        fields = [
            'subject', 'question_text', 'question_type', 'marks',
            'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        if question_type == 'mcq':
            options = [
                cleaned_data.get('option_a'),
                cleaned_data.get('option_b'),
                cleaned_data.get('option_c'),
                cleaned_data.get('option_d'),
            ]
            if not all(options):
                raise forms.ValidationError("All options are required for MCQ questions.")
            
            if not cleaned_data.get('correct_answer'):
                raise forms.ValidationError("Correct answer is required for MCQ questions.")
        
        return cleaned_data


class QuestionPaperForm(forms.ModelForm):
    """Form for creating/updating question papers."""
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = QuestionPaper
        fields = ['title', 'subject', 'questions', 'total_marks', 
                  'duration_minutes', 'passing_marks', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter questions by selected subject
        if self.instance.pk:
            self.fields['questions'].queryset = Question.objects.filter(
                subject=self.instance.subject
            )


class ExamScheduleForm(forms.ModelForm):
    """Form for scheduling exams."""
    assigned_students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = ExamSchedule
        fields = ['question_paper', 'scheduled_date', 'start_time', 
                  'end_time', 'assigned_students', 'status']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class StudentExamAnswerForm(forms.Form):
    """Dynamic form for student to answer exam questions."""
    
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.question_type == 'mcq':
                choices = [
                    ('a', question.option_a),
                    ('b', question.option_b),
                    ('c', question.option_c),
                    ('d', question.option_d),
                ]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=False
                )
            else:  # descriptive
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    widget=forms.Textarea(attrs={'rows': 5}),
                    required=False
                )
