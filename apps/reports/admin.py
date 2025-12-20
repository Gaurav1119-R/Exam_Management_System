"""
Admin configuration for reports app.
"""
from django.contrib import admin
from .models import ProjectReport, StudentReport


@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'status', 'submission_date', 'marks_obtained')
    list_filter = ('status', 'submission_date')
    search_fields = ('student__enrollment_number', 'title')
    readonly_fields = ('submission_date', 'created_at', 'updated_at')


@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'overall_score', 'overall_performance', 'updated_at')
    list_filter = ('overall_performance',)
    search_fields = ('student__enrollment_number',)
    readonly_fields = ('updated_at',)
