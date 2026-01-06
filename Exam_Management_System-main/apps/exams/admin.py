"""
Admin configuration for exams app.
"""
from django.contrib import admin
from .models import Department, Subject, Question, QuestionPaper, ExamSchedule, StudentExamResponse, StudentExamResult


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits', 'created_at')
    search_fields = ('code', 'name')
    list_filter = ('department',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'question_type', 'marks', 'created_at')
    list_filter = ('subject', 'question_type')
    search_fields = ('question_text',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'total_marks', 'duration_minutes', 'created_at')
    filter_horizontal = ('questions',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('question_paper', 'scheduled_date', 'start_time', 'status')
    list_filter = ('status', 'scheduled_date')
    filter_horizontal = ('assigned_students',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudentExamResponse)
class StudentExamResponseAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_schedule', 'question', 'marks_obtained')
    list_filter = ('exam_schedule', 'marks_obtained')
    search_fields = ('student__enrollment_number',)
    readonly_fields = ('exam_schedule', 'student', 'question', 'answered_at')


@admin.register(StudentExamResult)
class StudentExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_schedule', 'percentage', 'status')
    list_filter = ('status', 'graded_at')
    search_fields = ('student__enrollment_number',)
    readonly_fields = ('graded_at',)
