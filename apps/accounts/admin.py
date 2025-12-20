"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role filtering."""
    list_display = ('username', 'email', 'first_name', 'role', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone_number')}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Student profile admin."""
    list_display = ('enrollment_number', 'user', 'department', 'semester', 'is_active')
    list_filter = ('department', 'semester', 'is_active')
    search_fields = ('enrollment_number', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('enrollment_number', 'department', 'semester')
        }),
        ('Personal Information', {
            'fields': ('profile_picture', 'date_of_birth', 'address')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
