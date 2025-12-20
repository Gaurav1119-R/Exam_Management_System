"""
Views for user authentication and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import IntegrityError
import random
import logging
from django.utils import timezone
from .models import User, StudentProfile

logger = logging.getLogger(__name__)
from .forms import (
    CustomUserCreationForm, StudentRegistrationForm, 
    LoginForm, StudentProfileForm
)


def _generate_username_from_email(email):
    """Generate a unique username based on the local part of the email."""
    base = email.split('@')[0]
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1
    return username


def register_view(request):
    """Registration choice page — lets user choose Student or Admin registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'accounts/register_choice.html')


def student_register_view(request):
    """Student-only registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate username automatically
            user.username = _generate_username_from_email(form.cleaned_data.get('email'))
            user.role = 'student'
            user.save()

            # Generate a unique enrollment number using the user's pk and a random suffix
            def _generate_enrollment_number(user):
                base = str(user.pk)
                while True:
                    candidate = base + str(random.randint(1000, 9999))
                    if not StudentProfile.objects.filter(enrollment_number=candidate).exists():
                        return candidate

            enrollment_number = _generate_enrollment_number(user)
            default_department = 'Undeclared'

            # Create StudentProfile. Semester defaults to 1 when omitted.
            try:
                StudentProfile.objects.create(
                    user=user,
                    enrollment_number=enrollment_number,
                    department=default_department,
                    semester=1
                )
            except IntegrityError:
                # Roll back the created user to avoid orphan user record
                user.delete()
                form.add_error(None, 'Could not create student profile. Please try again.')
                return render(request, 'accounts/register_student.html', {'form': form})

            messages.success(request, 'Student account created successfully! Please log in.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register_student.html', {'form': form})


def admin_register_view(request):
    """Admin-only registration view. Auto-login after successful registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate and set a username from email
            user.username = _generate_username_from_email(form.cleaned_data.get('email'))
            user.role = 'admin'
            user.save()

            # Auto-login the newly created admin and redirect to admin dashboard
            auth_user = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data.get('password1')
            )
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, 'Admin account created and logged in!')
                return redirect('exams:admin:dashboard')

            messages.success(request, 'Admin account created successfully! Please login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register_admin.html', {'form': form})

def login_view(request):
    """
    User login view - authenticates user and redirects to dashboard.
    
    GET: Display login form
    POST: Process login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # First try authenticating using the provided identifier directly
            user = authenticate(request, username=username_or_email, password=password)

            # If that fails, and the input looks like an email, try to find user by email
            if user is None:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                except User.DoesNotExist:
                    user_obj = None

                if user_obj is not None:
                    user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Log out user and redirect to login page."""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Main dashboard view - redirects to role-specific dashboard.
    
    - Admin: Admin portal
    - Student: Student portal
    """
    if request.user.is_admin_user:
        return redirect('exams:admin:dashboard')
    elif request.user.is_student_user:
        return redirect('exams:student:dashboard')
    
    return render(request, 'accounts/dashboard.html')


@login_required
def profile_view(request):
    """Display user profile information."""
    if request.user.is_student_user:
        # Ensure there is a StudentProfile (helper in exams.views returns/creates one)
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            # Lazy create a minimal profile similar to exams._ensure_student_profile
            base = str(request.user.pk)
            candidate = base + str(random.randint(1000, 9999))
            # ensure candidate uniqueness
            while StudentProfile.objects.filter(enrollment_number=candidate).exists():
                candidate = base + str(random.randint(1000, 9999))
            student_profile = StudentProfile.objects.create(
                user=request.user,
                enrollment_number=candidate,
                department='Undeclared',
                semester=1
            )

        # Build a safe student dict with fallbacks for missing data
        student = {
            'name': request.user.get_full_name() or request.user.username,
            'enrollment_number': student_profile.enrollment_number or '-',
            'department': student_profile.department or 'Not Yet Declared',
            'semester': student_profile.semester if student_profile.semester is not None else 'N/A',
            'email': request.user.email,
            'profile_picture': getattr(student_profile, 'profile_picture', None)
        }

        # Debug: log profile fields to help diagnose blank values
        logger.debug('Profile view for user %s: enrollment=%s, department=%s, semester=%s',
                     request.user.pk, student['enrollment_number'], student['department'], student['semester'])

        # Compute exam counts and serialize a small set of exams for the profile page
        schedules = student_profile.exam_schedules.select_related('question_paper__subject').all()
        now = timezone.now()
        upcoming_qs = schedules.filter(scheduled_date__gte=now.date()).order_by('scheduled_date', 'start_time')[:6]
        past_qs = schedules.filter(scheduled_date__lt=now.date()).order_by('-scheduled_date', '-start_time')[:6]

        def _serialize_schedule(s):
            paper = s.question_paper
            return {
                'id': s.id,
                'is_live': s.is_exam_time(),
                'date': s.scheduled_date.strftime('%b %d, %Y'),
                'time_range': f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}",
                'duration': f"{paper.duration_minutes} min",
                'marks': paper.get_total_marks() or paper.total_marks,
                'subject': paper.subject.name,
            }

        upcoming_exams = [_serialize_schedule(s) for s in upcoming_qs]
        past_exams = [_serialize_schedule(s) for s in past_qs]

        context = {
            'student': student,
            'student_profile': student_profile,
            'profile': student_profile,
            'total_exams': schedules.count(),
            'upcoming_count': len(upcoming_exams),
            'past_count': len(past_exams),
            'upcoming_exams': upcoming_exams,
            'past_exams': past_exams,
        }
        return render(request, 'accounts/student_profile.html', context)

    # Admin/superuser: render a concise admin profile page
    if request.user.is_admin_user:
        user = request.user
        context = {
            'user': user,
            'role': user.role.title(),
            'joined': user.date_joined.strftime('%b %d, %Y'),
        }
        return render(request, 'accounts/admin_profile.html', context)

    return render(request, 'accounts/profile.html')


@login_required
def profile_update_view(request):
    """Update student profile information and user basic fields."""
    if not request.user.is_student_user:
        messages.error(request, 'Only students can update their profile.')
        return redirect('dashboard')
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            # Log incoming POST for debugging
            logger.debug('Profile update POST data: %s', {k: request.POST.get(k) for k in request.POST.keys()})

            # Prevent changing enrollment_number accidentally via the form
            profile_obj = form.save(commit=False)
            profile_obj.enrollment_number = student_profile.enrollment_number
            profile_obj.save()

            # Update basic User fields from the form inputs
            new_first = request.POST.get('first_name', request.user.first_name).strip()
            new_last = request.POST.get('last_name', request.user.last_name).strip()
            new_email = request.POST.get('email', request.user.email).strip()
            new_phone = request.POST.get('phone_number', request.user.phone_number or '').strip()

            # Check for email uniqueness if changed
            if new_email != request.user.email and User.objects.filter(email__iexact=new_email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Email already in use by another account.')
                logger.warning('Email conflict when updating profile for user %s: %s', request.user.pk, new_email)
                return render(request, 'accounts/profile_update.html', {'form': form, 'user': request.user})

            user = request.user
            user.first_name = new_first
            user.last_name = new_last
            user.email = new_email
            user.phone_number = new_phone
            user.save()

            # Refresh the student_profile instance so subsequent reads are up-to-date
            student_profile.refresh_from_db()

            logger.info('Profile updated for user %s (enrollment %s)', user.pk, student_profile.enrollment_number)

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            # If form invalid, render template with form errors visible
            messages.error(request, 'There were errors updating your profile. Please correct them below.')
            return render(request, 'accounts/profile_update.html', {'form': form, 'user': request.user})
    else:
        form = StudentProfileForm(instance=student_profile)
    
    return render(request, 'accounts/profile_update.html', {'form': form, 'user': request.user})


def csrf_failure(request, reason=''):
    """Friendly CSRF failure view for users.

    Django's default CSRF debug page is useful in development but can be
    confusing. This view provides a concise message and action items.
    """
    context = {
        'reason': reason,
    }
    # Show a simple explanation and action items; keep status 403
    return render(request, '403_csrf.html', context=context, status=403)