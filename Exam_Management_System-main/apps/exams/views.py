"""
Views for exam management (admin portal) and exam taking (student portal).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import random
from .models import (
    Subject, Question, QuestionPaper, ExamSchedule,
    StudentExamResponse, StudentExamResult, Department
)
from apps.accounts.models import StudentProfile
from .forms import (
    SubjectForm, QuestionForm, QuestionPaperForm,
    ExamScheduleForm, StudentExamAnswerForm
)


def is_ajax(request):
    """Check if request is AJAX (XMLHttpRequest)."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


@require_http_methods(["GET"])
def get_subjects_by_department(request):
    """
    AJAX endpoint to fetch subjects for a selected department.
    Returns JSON with list of subjects.
    """
    department_code = request.GET.get('department', None)
    
    if not department_code:
        return JsonResponse({'error': 'Department not provided'}, status=400)
    
    try:
        department = Department.objects.get(code=department_code)
        subjects = Subject.objects.filter(department=department).values('id', 'code', 'name')
        return JsonResponse({
            'success': True,
            'subjects': list(subjects)
        })
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
    """Admin dashboard overview with dynamic data."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get counts from database
    total_subjects = Subject.objects.count()
    total_questions = Question.objects.count()
    total_papers = QuestionPaper.objects.count()
    total_schedules = ExamSchedule.objects.count()
    
    # Get student count
    from apps.accounts.models import StudentProfile
    total_students = StudentProfile.objects.count()
    
    # Get today's schedules count
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    schedules_today = ExamSchedule.objects.filter(scheduled_date=today).count()
    
    # Get this month's new subjects (created in last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    subjects_this_month = Subject.objects.filter(created_at__gte=thirty_days_ago).count() if hasattr(Subject, 'created_at') else 0
    
    # Get this month's new questions
    questions_this_month = Question.objects.filter(created_at__gte=thirty_days_ago).count() if hasattr(Question, 'created_at') else 0
    
    # Get this month's new students
    students_this_month = StudentProfile.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'total_subjects': total_subjects,
        'total_questions': total_questions,
        'total_papers': total_papers,
        'total_schedules': total_schedules,
        'total_students': total_students,
        'active_papers': total_papers,
        'subjects_this_month': subjects_this_month,
        'questions_this_month': questions_this_month,
        'students_this_month': students_this_month,
        'schedules_today': schedules_today,
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
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Subject created successfully!'})
            messages.success(request, 'Subject created successfully!')
            return redirect('exams:admin:subject_list')
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = SubjectForm()
    
    if is_ajax(request):
        return render(request, 'exams/admin/partials/subject_form_partial.html', {'form': form})
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
        if is_ajax(request):
            return JsonResponse({'success': False, 'error': 'Access denied.'}, status=403)
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            if is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'message': 'Question created successfully!',
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'marks': question.marks,
                })
            messages.success(request, 'Question created successfully!')
            return redirect('exams:admin:question_list')
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = QuestionForm()
    
    if is_ajax(request):
        return render(request, 'exams/admin/partials/question_form_partial.html', {'form': form})
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
            
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Question paper created successfully!'})
            messages.success(request, 'Question paper created successfully! Now publish it to students.')
            return redirect('exams:admin:paper_list')
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = QuestionPaperForm()
    
    all_questions = Question.objects.select_related('subject').all()
    if is_ajax(request):
        return render(request, 'exams/admin/partials/paper_form_partial.html', {'form': form, 'all_questions': all_questions, 'departments': Department.objects.all()})
    return render(request, 'exams/admin/paper_form.html', {'form': form, 'all_questions': all_questions, 'departments': Department.objects.all()})


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
                  {'form': form, 'paper': paper, 'all_questions': all_questions, 'departments': Department.objects.all()})


@login_required
def paper_publish(request, pk):
    """Publish a question paper to students by creating an exam schedule."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    paper = get_object_or_404(QuestionPaper, pk=pk)
    
    if request.method == 'POST':
        selected_students_ids = request.POST.getlist('students')
        scheduled_date = request.POST.get('scheduled_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if not selected_students_ids:
            messages.error(request, 'Please select at least one student.')
            return redirect('exams:admin:paper_publish', pk=pk)
        
        if not scheduled_date or not start_time or not end_time:
            messages.error(request, 'Please fill in all date and time fields.')
            return redirect('exams:admin:paper_publish', pk=pk)
        
        try:
            from datetime import datetime
            scheduled_date_obj = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            # Create exam schedule
            schedule = ExamSchedule.objects.create(
                question_paper=paper,
                scheduled_date=scheduled_date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                status='published'
            )
            
            # Assign students - convert string IDs to integers
            students = StudentProfile.objects.filter(id__in=[int(sid) for sid in selected_students_ids])
            schedule.assigned_students.set(students)
            
            messages.success(request, f'Paper published to {students.count()} students successfully!')
            return redirect('exams:admin:paper_list')
        except Exception as e:
            messages.error(request, f'Error publishing paper: {str(e)}')
            return redirect('exams:admin:paper_publish', pk=pk)
    
    # Get request - show publish form
    all_students = StudentProfile.objects.all().order_by('enrollment_number')
    context = {
        'paper': paper,
        'students': all_students,
    }
    return render(request, 'exams/admin/paper_publish.html', context)


@login_required
def exam_schedules_debug(request):
    """Debug view to check exam schedule assignments."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Handle manual assignment
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        student_ids = request.POST.getlist('students')
        
        if schedule_id and student_ids:
            schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
            students = StudentProfile.objects.filter(id__in=student_ids)
            schedule.assigned_students.add(*students)
            messages.success(request, f'Added {students.count()} students to {schedule.question_paper.title}')
            return redirect('exams:admin:schedules_debug')
    
    # Get all schedules with their assignments
    schedules = ExamSchedule.objects.all().select_related('question_paper__subject').prefetch_related('assigned_students').order_by('-scheduled_date')
    
    # Group by student to see what they have access to
    all_students = StudentProfile.objects.all().order_by('enrollment_number')
    
    # Search for specific student
    search_enrollment = request.GET.get('search', '')
    search_result = None
    if search_enrollment:
        search_result = StudentProfile.objects.filter(enrollment_number=search_enrollment).first()
    
    context = {
        'schedules': schedules,
        'all_students': all_students,
        'search_enrollment': search_enrollment,
        'search_result': search_result,
    }
    return render(request, 'exams/admin/schedules_debug.html', context)


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
            if is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Exam scheduled successfully!'})
            messages.success(request, 'Exam scheduled successfully!')
            return redirect('exams:admin:schedule_list')
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ExamScheduleForm()
    
    if is_ajax(request):
        return render(request, 'exams/admin/partials/schedule_form_partial.html', {'form': form})
    return render(request, 'exams/admin/schedule_form.html', {'form': form})


# ============================================================================
# STUDENT VIEWS
# ============================================================================

@login_required
def student_dashboard(request):
    """Student dashboard showing exam schedule with enhanced metrics."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student_profile = _ensure_student_profile(request.user)

    # Get assigned exams with related paper & subject to avoid extra queries
    schedules = student_profile.exam_schedules.select_related('question_paper__subject').all()

    # Get IDs of exams that student has completed
    completed_exam_ids = StudentExamResult.objects.filter(
        student=student_profile
    ).values_list('exam_schedule_id', flat=True)

    # Fetch schedules and convert to list for Python-side classification
    schedules_list = list(schedules)

    now = timezone.now()
    upcoming_list = []
    past_list = []

    for s in schedules_list:
        # Completed exams are considered past
        if s.id in completed_exam_ids:
            past_list.append(s)
            continue
        try:
            start_dt = timezone.make_aware(datetime.combine(s.scheduled_date, s.start_time))
            end_dt = timezone.make_aware(datetime.combine(s.scheduled_date, s.end_time))
        except Exception:
            # Fallback: date-only checks
            if s.scheduled_date >= now.date():
                upcoming_list.append(s)
            else:
                past_list.append(s)
            continue

        # Consider it upcoming if it hasn't ended yet (covers ongoing exams even if scheduled_date was yesterday)
        if end_dt >= now or start_dt >= now:
            upcoming_list.append(s)
        else:
            past_list.append(s)

    # Order upcoming by start date/time and past by most recent
    upcoming_qs = sorted(upcoming_list, key=lambda x: (x.scheduled_date, x.start_time))
    past_qs = sorted(past_list, key=lambda x: (x.scheduled_date, x.start_time), reverse=True)

    def serialize_schedule(s):
        paper = s.question_paper
        # Try to fetch student's result for this schedule
        try:
            student_result = StudentExamResult.objects.get(exam_schedule=s, student=student_profile)
        except StudentExamResult.DoesNotExist:
            student_result = None

        return {
            'id': s.id,
            'is_live': s.is_exam_time(),
            'date': s.scheduled_date.strftime('%b %d, %Y'),
            'time_range': f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}",
            'duration': f"{paper.duration_minutes} min",
            'marks': paper.get_total_marks() or paper.total_marks,
            'subject': paper.subject.name,
            'score': student_result.marks_obtained if student_result is not None else None,
            'percentage': student_result.percentage if student_result is not None else None,
            'passed': True if (student_result and student_result.status == 'passed') else False,
            'status': student_result.status if student_result is not None else 'pending',
        }

    upcoming_exams = [serialize_schedule(s) for s in upcoming_qs]
    past_exams = [serialize_schedule(s) for s in past_qs]

    # Calculate progress percentage
    total = len(schedules_list)
    progress_percentage = int((len(past_qs) / total * 100)) if total > 0 else 0

    context = {
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
        'total_exams': total,
        'upcoming_count': len(upcoming_exams),
        'past_count': len(past_exams),
        'progress_percentage': progress_percentage,
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
    
    # Get questions from the question paper
    questions = schedule.question_paper.questions.all()
    
    if request.method == 'POST':
        form = StudentExamAnswerForm(questions, request.POST)
        if form.is_valid():
            # Save responses and auto-grade MCQs
            marks_obtained = 0
            
            for question in questions:
                field_name = f'question_{question.id}'
                answer = form.cleaned_data.get(field_name, '')
                
                # Save response
                StudentExamResponse.objects.update_or_create(
                    exam_schedule=schedule,
                    student=student_profile,
                    question=question,
                    defaults={'student_answer': answer}
                )
                
                # Auto-grade MCQs
                if question.question_type == 'mcq' and answer:
                    # Check if answer matches correct answer
                    if answer.lower() == question.correct_answer.lower():
                        marks_obtained += question.marks
            
            # Calculate marks and percentage
            paper = schedule.question_paper
            total_marks = paper.get_total_marks() or paper.total_marks
            percentage = 0 if total_marks == 0 else (marks_obtained / total_marks * 100)
            
            # Determine pass/fail status
            passing_marks = paper.passing_marks
            if percentage >= passing_marks:
                status = 'passed'
            else:
                status = 'failed'
            
            StudentExamResult.objects.update_or_create(
                exam_schedule=schedule,
                student=student_profile,
                defaults={
                    'total_marks': total_marks,
                    'marks_obtained': marks_obtained,
                    'percentage': percentage,
                    'status': status,
                    'graded_at': timezone.now()
                }
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
    ).select_related('question')
    
    # Compute performance breakdown
    questions_attempted = responses.count()
    total_questions = schedule.question_paper.questions.count() if schedule.question_paper else 0
    correct_answers = 0
    incorrect_answers = 0
    skipped_questions = 0

    for resp in responses:
        if resp.marks_obtained is None:
            skipped_questions += 1
        else:
            if resp.marks_obtained >= getattr(resp.question, 'marks', 0):
                correct_answers += 1
            else:
                incorrect_answers += 1

    # If some questions missing (no response), count as skipped
    skipped_questions = skipped_questions + (total_questions - questions_attempted) if total_questions > questions_attempted else skipped_questions

    correct_percentage = int((correct_answers / total_questions * 100)) if total_questions > 0 else 0
    incorrect_percentage = int((incorrect_answers / total_questions * 100)) if total_questions > 0 else 0
    skipped_percentage = int((skipped_questions / total_questions * 100)) if total_questions > 0 else 0

    context = {
        'result': result,
        'responses': responses,
        'exam_schedule': schedule,
        'questions_attempted': questions_attempted,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'skipped_questions': skipped_questions,
        'correct_percentage': correct_percentage,
        'incorrect_percentage': incorrect_percentage,
        'skipped_percentage': skipped_percentage,
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


# ============================================================================
# ADMIN GRADING VIEWS
# ============================================================================

@login_required
def exam_submissions_list(request):
    """List all exam schedules with submission counts."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get all exam schedules with related data
    schedules = ExamSchedule.objects.select_related(
        'question_paper__subject'
    ).all().order_by('-scheduled_date')
    
    # Add submission count to each schedule
    schedules_data = []
    for schedule in schedules:
        response_count = StudentExamResponse.objects.filter(
            exam_schedule=schedule
        ).values('student').distinct().count()
        
        result_count = StudentExamResult.objects.filter(
            exam_schedule=schedule
        ).count()
        
        schedules_data.append({
            'schedule': schedule,
            'total_responses': response_count,
            'graded_count': StudentExamResult.objects.filter(
                exam_schedule=schedule
            ).exclude(status='pending').count(),
            'pending_count': StudentExamResult.objects.filter(
                exam_schedule=schedule,
                status='pending'
            ).count(),
        })
    
    context = {
        'schedules_data': schedules_data,
    }
    return render(request, 'exams/admin/exam_submissions_list.html', context)


@login_required
def exam_submissions_detail(request, schedule_id):
    """View all student submissions for a specific exam."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    
    # Get all student responses for this exam
    results = StudentExamResult.objects.filter(
        exam_schedule=schedule
    ).select_related('student__user').order_by('student__enrollment_number')
    
    context = {
        'schedule': schedule,
        'results': results,
    }
    return render(request, 'exams/admin/exam_submissions_detail.html', context)


@login_required
def grade_exam_submission(request, schedule_id, student_id):
    """Grade a specific student's exam submission."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    student_profile = get_object_or_404(StudentProfile, pk=student_id)
    
    # Get exam result
    result = get_object_or_404(
        StudentExamResult,
        exam_schedule=schedule,
        student=student_profile
    )
    
    # Get all responses for this exam
    paper = schedule.question_paper
    questions = paper.questions.all()
    
    responses_data = []
    for question in questions:
        try:
            response = StudentExamResponse.objects.get(
                exam_schedule=schedule,
                student=student_profile,
                question=question
            )
        except StudentExamResponse.DoesNotExist:
            response = None
        
        responses_data.append({
            'question': question,
            'response': response,
        })
    
    if request.method == 'POST':
        # Process marking
        total_marks = 0
        
        for question in questions:
            marks_key = f'marks_{question.id}'
            if marks_key in request.POST:
                try:
                    marks_str = request.POST[marks_key].strip()
                    if marks_str:  # Only process if not empty
                        marks = int(marks_str)
                        response = StudentExamResponse.objects.get(
                            exam_schedule=schedule,
                            student=student_profile,
                            question=question
                        )
                        response.marks_obtained = marks
                        response.save()
                        total_marks += marks
                except (ValueError, StudentExamResponse.DoesNotExist) as e:
                    pass
        
        # Calculate percentage
        total_exam_marks = paper.get_total_marks() or paper.total_marks
        percentage = (total_marks / total_exam_marks * 100) if total_exam_marks > 0 else 0
        
        # Check if admin manually selected pass/fail
        final_status = request.POST.get('final_status', '').strip().lower()
        
        if final_status in ['passed', 'failed']:
            # Use admin's manual selection
            status = final_status
        else:
            # Use automatic calculation based on percentage (paper.passing_marks is a percentage)
            status = 'passed' if percentage >= paper.passing_marks else 'failed'
        
        # Update result
        result.total_marks = total_exam_marks
        result.marks_obtained = total_marks
        result.percentage = percentage
        result.status = status
        result.graded_at = timezone.now()
        result.save()
        
        messages.success(request, f'Marks saved for {student_profile.user.get_full_name()}! Status: {status.upper()}')
        return redirect('exams:admin:submissions_detail', schedule_id=schedule_id)
    
    context = {
        'schedule': schedule,
        'student_profile': student_profile,
        'result': result,
        'responses_data': responses_data,
        'paper': paper,
    }
    return render(request, 'exams/admin/grade_exam_submission.html', context)


# URL Pattern mapping

@login_required
def student_subject_list(request):
    """List subjects for the logged-in student filtered by department."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    student_profile = _ensure_student_profile(request.user)
    dept_code = student_profile.department

    if dept_code and dept_code != 'Undeclared':
        subjects = Subject.objects.filter(department__code=dept_code).order_by('name')
        department_name = None
        try:
            department_name = subjects.first().department.name if subjects.exists() else dept_code
        except Exception:
            department_name = dept_code
    else:
        subjects = Subject.objects.all().order_by('department__name', 'name')
        department_name = 'All Departments'

    context = {
        'subjects': subjects,
        'department_name': department_name,
    }
    return render(request, 'exams/student/subject_list.html', context)


admin = type('obj', (object,), {
    'dashboard': admin_dashboard,
})
student = type('obj', (object,), {
    'dashboard': student_dashboard,
    'exam_take': exam_take,
    'exam_result': exam_result,
    'subjects': student_subject_list,
})
