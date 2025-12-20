"""
Views for attendance management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
import csv
import calendar
from datetime import timedelta, datetime

from apps.exams.models import ExamSchedule
from apps.accounts.models import StudentProfile
from .models import Attendance, AttendanceReport
from .forms import AttendanceForm


@login_required
def mark_attendance(request, schedule_id):
    """Mark attendance for exam."""
    if not request.user.is_admin_user:
        messages.error(request, 'Only admins can mark attendance.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    students = schedule.assigned_students.all()
    
    if request.method == 'POST':
        for student in students:
            attended = request.POST.get(f'student_{student.id}') == 'on'
            
            attendance, created = Attendance.objects.update_or_create(
                exam_schedule=schedule,
                student=student,
                defaults={
                    'attended': attended,
                    'marked_by': request.user,
                }
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance:report', schedule_id=schedule_id)
    
    context = {
        'schedule': schedule,
        'students': students,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def attendance_report(request, schedule_id):
    """View attendance report for exam."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    attendances = Attendance.objects.filter(exam_schedule=schedule)
    
    total_students = schedule.assigned_students.count()
    present_count = attendances.filter(attended=True).count()
    absent_count = attendances.filter(attended=False).count()
    
    context = {
        'schedule': schedule,
        'attendances': attendances,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
    }
    return render(request, 'attendance/attendance_report.html', context)


@login_required
def student_attendance_report(request):
    """View attendance report for logged-in student."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Support filtering via ?filter=last30|term|all
    filter_type = request.GET.get('filter', 'all')
    now = timezone.now().date()

    # Get current student's attendances
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    attendances = Attendance.objects.filter(student=student_profile).select_related('exam_schedule__question_paper__subject')

    if filter_type == 'last30':
        since = now - timedelta(days=30)
        attendances_qs = attendances.filter(exam_schedule__scheduled_date__gte=since)
    elif filter_type == 'term':
        # For simplicity, assume term is 6 months back — adapt if you have real term model
        since = now - timedelta(days=180)
        attendances_qs = attendances.filter(exam_schedule__scheduled_date__gte=since)
    else:
        attendances_qs = attendances

    total_exams = attendances_qs.count()
    present_count = attendances_qs.filter(attended=True).count()
    absent_count = total_exams - present_count

    present_percentage = (present_count / total_exams * 100) if total_exams > 0 else 0
    absent_percentage = (absent_count / total_exams * 100) if total_exams > 0 else 0

    # Build a simple list of rows for template display
    attendance_rows = []
    for a in attendances_qs.order_by('-exam_schedule__scheduled_date'):
        s = a.exam_schedule
        paper = getattr(s, 'question_paper', None)
        subject = paper.subject.name if paper and getattr(paper, 'subject', None) else 'N/A'
        time_range = ''
        try:
            time_range = f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}"
        except Exception:
            time_range = ''
        attendance_rows.append({
            'subject': subject,
            'date': s.scheduled_date,
            'time_range': time_range,
            'attended': a.attended,
        })

    # Month-wise trends (last 6 months)
    months = []
    month_labels = []
    present_values = []
    total_values = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=now.day - 1) - timedelta(days=30 * i)
        y = month_date.year
        m = month_date.month
        month_label = f"{calendar.month_abbr[m]} {y}"
        month_labels.append(month_label)
        months.append((y, m))

    for (y, m) in months:
        month_qs = attendances_qs.filter(exam_schedule__scheduled_date__year=y, exam_schedule__scheduled_date__month=m)
        total_m = month_qs.count()
        present_m = month_qs.filter(attended=True).count()
        total_values.append(total_m)
        present_values.append(present_m)

    # Flag to indicate whether there is any month-wise data to show in chart
    has_month_data = any(v > 0 for v in total_values)

    context = {
        'attendances': attendances_qs,
        'attendance_rows': attendance_rows,
        'total_exams': total_exams,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': present_percentage,
        'present_percentage': present_percentage,
        'absent_percentage': absent_percentage,
        'filter_type': filter_type,
        'month_labels': month_labels,
        'present_values': present_values,
        'total_values': total_values,
        'has_month_data': has_month_data,
    }
    return render(request, 'attendance/student_attendance_report.html', context)


@login_required
def student_attendance_export(request):
    """Export student's attendance as CSV, supports same filters as report."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student_profile = get_object_or_404(StudentProfile, user=request.user)
    attendances = Attendance.objects.filter(student=student_profile).select_related('exam_schedule__question_paper__subject')

    filter_type = request.GET.get('filter', 'all')
    now = timezone.now().date()

    if filter_type == 'last30':
        since = now - timedelta(days=30)
        attendances = attendances.filter(exam_schedule__scheduled_date__gte=since)
    elif filter_type == 'term':
        since = now - timedelta(days=180)
        attendances = attendances.filter(exam_schedule__scheduled_date__gte=since)

    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Subject', 'Time', 'Status'])

    for a in attendances.order_by('exam_schedule__scheduled_date'):
        s = a.exam_schedule
        paper = getattr(s, 'question_paper', None)
        subject = paper.subject.name if paper and getattr(paper, 'subject', None) else 'N/A'
        try:
            time_range = f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}"
        except Exception:
            time_range = ''
        status = 'Present' if a.attended else 'Absent'
        writer.writerow([s.scheduled_date.isoformat(), subject, time_range, status])

    return response


def admin_attendance(request):
    return render(request, 'attendance/admin_attendance.html')