"""
Views for exam management (admin portal) and exam taking (student portal).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
import random
from .models import (
    Subject, Question, QuestionPaper, ExamSchedule,
    StudentExamResponse, StudentExamResult
)
from apps.accounts.models import StudentProfile
from .forms import (
    SubjectForm, QuestionForm, QuestionPaperForm,
    ExamScheduleForm, StudentExamAnswerForm
)


def _ensure_student_profile(user):
    """Return existing StudentProfile or create a minimal one if missing."""
    try:
        return user.student_profile
    except StudentProfile.DoesNotExist:
        base = str(user.pk)
        while True:
            candidate = base + str(random.randint(1000, 9999))
            if not StudentProfile.objects.filter(enrollment_number=candidate).exists():
                break
        profile = StudentProfile.objects.create(
            user=user,
            enrollment_number=candidate,
            department='Undeclared',
            semester=1
        )
        return profile


# ============================================================================
# ADMIN VIEWS
# ============================================================================

@login_required
def admin_dashboard(request):
    """Admin dashboard overview."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {
        'total_subjects': Subject.objects.count(),
        'total_questions': Question.objects.count(),
        'total_papers': QuestionPaper.objects.count(),
        'total_schedules': ExamSchedule.objects.count(),
    }
    return render(request, 'exams/admin/dashboard.html', context)


@require_http_methods(["GET"])
@login_required
def admin_dashboard_counts(request):
    """Return JSON counts for dashboard widgets (used by AJAX)."""
    if not request.user.is_admin_user:
        return JsonResponse({'error': 'Access denied.'}, status=403)
    data = {
        'total_subjects': Subject.objects.count(),
        'total_questions': Question.objects.count(),
        'total_papers': QuestionPaper.objects.count(),
        'total_schedules': ExamSchedule.objects.count(),
    }
    return JsonResponse(data)

# Subject Management
@login_required
def subject_list(request):
    """List all subjects."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    subjects = Subject.objects.all()
    return render(request, 'exams/admin/subject_list.html', {'subjects': subjects})


@login_required
def subject_create(request):
    """Create new subject."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('exams:admin:subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'exams/admin/subject_form.html', {'form': form})


@login_required
def subject_update(request, pk):
    """Update subject."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('exams:admin:subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'exams/admin/subject_form.html', 
                  {'form': form, 'subject': subject})


@login_required
def subject_delete(request, pk):
    """Delete subject."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('exams:admin:subject_list')
    
    return render(request, 'exams/admin/subject_confirm_delete.html', 
                  {'subject': subject})


# Question Management
@login_required
def question_list(request):
    """List all questions with filters."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    questions = Question.objects.all()
    subject_filter = request.GET.get('subject')
    question_type_filter = request.GET.get('type')
    
    if subject_filter:
        questions = questions.filter(subject_id=subject_filter)
    if question_type_filter:
        questions = questions.filter(question_type=question_type_filter)
    
    subjects = Subject.objects.all()
    return render(request, 'exams/admin/question_list.html', {
        'questions': questions,
        'subjects': subjects,
    })


@login_required
def question_create(request):
    """Create new question."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            messages.success(request, 'Question created successfully!')
            return redirect('exams:admin:question_list')
    else:
        form = QuestionForm()
    
    return render(request, 'exams/admin/question_form.html', {'form': form})


@login_required
def question_update(request, pk):
    """Update question."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('exams:admin:question_list')
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'exams/admin/question_form.html', 
                  {'form': form, 'question': question})


@login_required
def question_delete(request, pk):
    """Delete question."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('exams:admin:question_list')
    
    return render(request, 'exams/admin/question_confirm_delete.html',
                  {'question': question})


# Question Paper Management
@login_required
def paper_list(request):
    """List all question papers."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    papers = QuestionPaper.objects.all()
    return render(request, 'exams/admin/paper_list.html', {'papers': papers})


@login_required
def paper_create(request):
    """Create new question paper."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QuestionPaperForm(request.POST)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.created_by = request.user
            paper.save()
            form.save_m2m()
            messages.success(request, 'Question paper created successfully!')
            return redirect('exams:admin:paper_list')
    else:
        form = QuestionPaperForm()
    
    all_questions = Question.objects.select_related('subject').all()
    return render(request, 'exams/admin/paper_form.html', {'form': form, 'all_questions': all_questions})


@login_required
def paper_update(request, pk):
    """Update question paper."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    paper = get_object_or_404(QuestionPaper, pk=pk)
    
    if request.method == 'POST':
        form = QuestionPaperForm(request.POST, instance=paper)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question paper updated successfully!')
            return redirect('exams:admin:paper_list')
    else:
        form = QuestionPaperForm(instance=paper)
    
    all_questions = Question.objects.select_related('subject').all()
    return render(request, 'exams/admin/paper_form.html',
                  {'form': form, 'paper': paper, 'all_questions': all_questions})


# Exam Schedule Management
@login_required
def schedule_list(request):
    """List all exam schedules."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedules = ExamSchedule.objects.all()
    return render(request, 'exams/admin/schedule_list.html', {'schedules': schedules})


@login_required
def schedule_create(request):
    """Create new exam schedule."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ExamScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam scheduled successfully!')
            return redirect('exams:admin:schedule_list')
    else:
        form = ExamScheduleForm()
    
    return render(request, 'exams/admin/schedule_form.html', {'form': form})


# ============================================================================
# STUDENT VIEWS
# ============================================================================

@login_required
def student_dashboard(request):
    """Student dashboard showing exam schedule."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student_profile = _ensure_student_profile(request.user)

    # Get assigned exams with related paper & subject to avoid extra queries
    schedules = student_profile.exam_schedules.select_related('question_paper__subject').all()

    # Categorize exams
    now = timezone.now()
    upcoming_qs = schedules.filter(scheduled_date__gte=now.date()).order_by('scheduled_date', 'start_time')
    past_qs = schedules.filter(scheduled_date__lt=now.date()).order_by('-scheduled_date', '-start_time')

    def serialize_schedule(s):
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

    upcoming_exams = [serialize_schedule(s) for s in upcoming_qs]
    past_exams = [serialize_schedule(s) for s in past_qs]

    context = {
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
        'total_exams': schedules.count(),
        'upcoming_count': len(upcoming_exams),
        'past_count': len(past_exams),
    }
    return render(request, 'exams/student/dashboard.html', context)


@login_required
def exam_take(request, schedule_id):
    """Student takes exam."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    student_profile = _ensure_student_profile(request.user)
    
    # Check if student is assigned
    if not schedule.assigned_students.filter(pk=student_profile.pk).exists():
        messages.error(request, 'You are not assigned to this exam.')
        return redirect('exams:student:dashboard')
    
    # Check exam time
    if not schedule.is_exam_time():
        messages.error(request, 'Exam is not available at this time.')
        return redirect('exams:student:dashboard')
    
    if request.method == 'POST':
        form = StudentExamAnswerForm(questions, request.POST)
        if form.is_valid():
            # Save responses
            for question in questions:
                field_name = f'question_{question.id}'
                answer = form.cleaned_data.get(field_name, '')
                
                StudentExamResponse.objects.update_or_create(
                    exam_schedule=schedule,
                    student=student_profile,
                    question=question,
                    defaults={'student_answer': answer}
                )
            
            messages.success(request, 'Exam submitted successfully!')
            return redirect('exams:student:exam_result', schedule_id=schedule_id)
    else:
        form = StudentExamAnswerForm(questions)
    
    context = {
        'schedule': schedule,
        'form': form,
        'questions': questions,
    }
    return render(request, 'exams/student/exam_take.html', context)


@login_required
def exam_result(request, schedule_id):
    """View exam result."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    student_profile = _ensure_student_profile(request.user)
    
    result = get_object_or_404(StudentExamResult, exam_schedule=schedule, student=student_profile)
    responses = StudentExamResponse.objects.filter(
        exam_schedule=schedule,
        student=student_profile
    )
    
    context = {
        'result': result,
        'responses': responses,
    }
    return render(request, 'exams/student/exam_result.html', context)


@login_required
def exam_history(request):
    """View exam history for student."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    student_profile = _ensure_student_profile(request.user)
    results = StudentExamResult.objects.filter(student=student_profile)
    
    context = {
        'results': results,
    }
    return render(request, 'exams/student/exam_history.html', context)


# URL Pattern mapping
admin = type('obj', (object,), {
    'dashboard': admin_dashboard,
})
student = type('obj', (object,), {
    'dashboard': student_dashboard,
    'exam_take': exam_take,
    'exam_result': exam_result,
})
