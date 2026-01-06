"""
Attendance tracking models.
"""
from django.db import models
from apps.accounts.models import StudentProfile
from apps.exams.models import ExamSchedule


class Attendance(models.Model):
    """
    Attendance model - tracks student attendance in exams.
    
    Fields:
        - exam_schedule: Foreign key to ExamSchedule
        - student: Foreign key to StudentProfile
        - attended: Boolean indicating presence
        - check_in_time: When student checked in
        - check_out_time: When student checked out
        - marked_by: Admin who marked attendance
    """
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    attended = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    marked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances'
    )
    marked_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('exam_schedule', 'student')
        ordering = ['-marked_at']
        indexes = [
            models.Index(fields=['exam_schedule', 'attended']),
        ]
    
    def __str__(self):
        status = "Present" if self.attended else "Absent"
        return f"{self.student.enrollment_number} - {self.exam_schedule} - {status}"


class AttendanceReport(models.Model):
    """
    AttendanceReport model - aggregated attendance statistics.
    
    Fields:
        - student: Foreign key to StudentProfile
        - total_exams: Total exams assigned
        - exams_attended: Exams attended
        - attendance_percentage: Calculated percentage
    """
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='attendance_report'
    )
    total_exams = models.IntegerField(default=0)
    exams_attended = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-attendance_percentage']
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.attendance_percentage}%"
    
    def calculate_percentage(self):
        """Calculate attendance percentage."""
        if self.total_exams == 0:
            return 0.0
        return (self.exams_attended / self.total_exams) * 100
