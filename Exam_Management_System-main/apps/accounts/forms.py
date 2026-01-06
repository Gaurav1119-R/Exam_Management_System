"""
Forms for user authentication and registration.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from .models import User, StudentProfile


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with email validation.

    Note: We intentionally omit the `username` field from the form and
    generate one automatically from the email to keep registration simple.
    """
    email = forms.EmailField(required=True)
    # Allow selecting a department for admin accounts during sign-up (optional)
    from .models import DEPARTMENT_CHOICES
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'department-select'})
    )
    
    class Meta:
        model = User
        # omit 'username' so users don't have to enter it
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'department')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style common fields and add placeholders for a better UX
        for fld, placeholder in [('email', 'you@example.com'), ('first_name', 'First name'), ('last_name', 'Last name')]:
            if fld in self.fields:
                self.fields[fld].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})

        # Ensure password fields use Bootstrap classes and show validator help text
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        # Show Django's password validation hints inline (guarded in case helper is missing)
        try:
            self.fields['password1'].help_text = password_validators_help_text_html()
        except Exception:
            # If the helper isn't available, fall back to empty help text
            self.fields['password1'].help_text = ''

        # Ensure the department field uses the select class when present
        if 'department' in self.fields:
            self.fields['department'].widget.attrs.update({'class': 'form-select', 'id': 'department-select'})


class LoginForm(forms.Form):
    """Simple login form."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile information."""
    
    class Meta:
        model = StudentProfile
        fields = ['enrollment_number', 'department', 'semester', 
                  'profile_picture', 'date_of_birth', 'address']
        widgets = {
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'department-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminUserForm(UserChangeForm):
    """Form for admin to manage users."""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email


class StudentRegistrationForm(CustomUserCreationForm):
    """Form for student registration with optional department selection.

    By default department was previously set to 'Undeclared'. We now allow the
    student to select a department during sign up (optional).
    """
    from .models import DEPARTMENT_CHOICES

    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'department-select'})
    )

    class Meta(CustomUserCreationForm.Meta):
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'department')


class LoginForm(forms.Form):
    """Simple login form."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile information."""
    
    class Meta:
        model = StudentProfile
        fields = ['enrollment_number', 'department', 'semester', 
                  'profile_picture', 'date_of_birth', 'address']
        widgets = {
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'department-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminUserForm(UserChangeForm):
    """Form for admin to manage users."""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'department', 'role', 'phone_number', 'is_active']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'})
        }
