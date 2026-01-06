"""
Admin configuration for attendance app.
"""
from django.contrib import admin
from .models import Attendance, AttendanceReport


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_schedule', 'attended', 'marked_at')
    list_filter = ('attended', 'marked_at', 'exam_schedule')
    search_fields = ('student__enrollment_number',)
    readonly_fields = ('marked_at',)


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_exams', 'exams_attended', 'attendance_percentage')
    list_filter = ('attendance_percentage',)
    search_fields = ('student__enrollment_number',)
    readonly_fields = ('updated_at',)
