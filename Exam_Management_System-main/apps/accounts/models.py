"""
User and StudentProfile models for authentication and authorization.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


# Department choices
DEPARTMENT_CHOICES = (
    ('BCA', 'BCA'),
    ('IT', 'IT'),
)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Fields:
        - username: Unique username for login
        - email: User's email address
        - first_name, last_name: User's name
        - is_admin: Boolean flag for admin role
        - is_student: Boolean flag for student role
        - profile_picture: User's profile image
        - phone_number: User's phone number
        - created_at: User creation timestamp
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )
    # Optional department for admins (students keep department in StudentProfile)
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='admin_profiles/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_admin_user(self):
        return self.role == 'admin'
    
    @property
    def is_student_user(self):
        return self.role == 'student'


class StudentProfile(models.Model):
    """
    Extended student profile information.
    
    One-to-One relationship with User model.
    
    Fields:
        - user: Foreign key to User model
        - enrollment_number: Unique enrollment ID
        - department: Academic department
        - semester: Current semester
        - profile_picture: Student's profile image
        - date_of_birth: Student's DOB
        - address: Residential address
        - is_active: Whether student is currently active
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    enrollment_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True
    )
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        default='BCA'
    )
    semester = models.IntegerField(choices=[(i, str(i)) for i in range(1, 9)])
    profile_picture = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['enrollment_number']
        indexes = [
            models.Index(fields=['enrollment_number']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.enrollment_number}"
