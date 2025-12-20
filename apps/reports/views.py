"""
Views for reports and analytics.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.models import StudentProfile
from apps.exams.models import StudentExamResult
from apps.attendance.models import Attendance
from .models import ProjectReport, StudentReport
from .forms import ProjectReportForm, StudentProjectReportForm, ProjectReportGradingForm


@login_required
def project_report_list(request):
    """List all project reports (admin view)."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    reports = ProjectReport.objects.all()
    status_filter = request.GET.get('status')
    
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    context = {
        'reports': reports,
    }
    return render(request, 'reports/admin/project_report_list.html', context)


@login_required
def project_report_create(request):
    """Create project report assignment (admin view)."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        student = get_object_or_404(StudentProfile, pk=student_id)
        
        form = ProjectReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.save()
            messages.success(request, 'Project report assigned successfully!')
            return redirect('project_report_list')
    else:
        form = ProjectReportForm()
    
    students = StudentProfile.objects.all()
    context = {
        'form': form,
        'students': students,
    }
    return render(request, 'reports/admin/project_report_form.html', context)


@login_required
def project_report_grade(request, report_id):
    """Grade project report (admin view)."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    report = get_object_or_404(ProjectReport, pk=report_id)
    
    if request.method == 'POST':
        form = ProjectReportGradingForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project report graded successfully!')
            return redirect('project_report_list')
    else:
        form = ProjectReportGradingForm(instance=report)
    
    context = {
        'form': form,
        'report': report,
    }
    return render(request, 'reports/admin/project_report_grading.html', context)


@login_required
def student_project_reports(request):
    """View assigned project reports (student view)."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    reports = ProjectReport.objects.filter(student=student_profile)
    
    context = {
        'projects': reports,
    }
    return render(request, 'reports/student/project_reports.html', context)


@login_required
def student_submit_project(request, report_id):
    """Submit project report (student view)."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    report = get_object_or_404(ProjectReport, pk=report_id)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    if report.student != student_profile:
        messages.error(request, 'This report does not belong to you.')
        return redirect('student_project_reports')
    
    if request.method == 'POST':
        form = StudentProjectReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.status = 'submitted'
            report.save()
            messages.success(request, 'Project report submitted successfully!')
            return redirect('student_project_reports')
    else:
        form = StudentProjectReportForm(instance=report)
    
    context = {
        'form': form,
        'report': report,
    }
    return render(request, 'reports/student/submit_project.html', context)


@login_required
def student_performance_report(request):
    """View overall performance report (student view)."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    
    # Calculate exam performance
    exam_results = StudentExamResult.objects.filter(student=student_profile)
    avg_exam_score = 0
    if exam_results.exists():
        total_percentage = sum(r.percentage for r in exam_results)
        avg_exam_score = total_percentage / exam_results.count()
    
    # Calculate project performance
    projects = ProjectReport.objects.filter(student=student_profile, status='graded')
    avg_project_score = 0
    if projects.exists():
        total_marks = sum(p.marks_obtained or 0 for p in projects)
        avg_project_score = (total_marks / projects.count())
    
    # Calculate attendance
    attendances = Attendance.objects.filter(student=student_profile)
    attendance_percentage = 0
    if attendances.exists():
        present_count = attendances.filter(attended=True).count()
        attendance_percentage = (present_count / attendances.count()) * 100
    
    context = {
        'exam_results': exam_results,
        'projects': projects,
        'attendances': attendances,
        'avg_exam_score': avg_exam_score,
        'avg_project_score': avg_project_score,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'reports/student/performance_report.html', context)
