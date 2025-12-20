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
    
    class Meta:
        model = User
        # omit 'username' so users don't have to enter it
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email


class StudentRegistrationForm(CustomUserCreationForm):
    """Form for student registration with profile information.

    Enrollment number and department are assigned automatically during account
    creation to simplify registration. The student can update department later
    from their profile settings.
    """
    class Meta(CustomUserCreationForm.Meta):
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


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
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminUserForm(UserChangeForm):
    """Form for admin to manage users."""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active']
