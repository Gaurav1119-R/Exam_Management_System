"""
Project reports and analytics models.
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.accounts.models import StudentProfile


class ProjectReport(models.Model):
    """
    ProjectReport model - stores student project submissions.
    
    Fields:
        - student: Foreign key to StudentProfile
        - title: Project title
        - description: Project description
        - file: Uploaded project file
        - submission_date: When project was submitted
        - due_date: Deadline for submission
        - marks_obtained: Marks awarded by admin
        - status: Submitted/Pending/Graded
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Submission'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late Submission'),
    )
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='project_reports'
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    file = models.FileField(
        upload_to='project_reports/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'zip', 'rar']
        )]
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    marks_obtained = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['student', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.title}"
    
    def is_late(self):
        """Check if submission is late."""
        from django.utils import timezone
        return self.submission_date.date() > self.due_date


class StudentReport(models.Model):
    """
    StudentReport model - aggregated performance report.
    
    Fields:
        - student: Foreign key to StudentProfile
        - average_exam_score: Average score across exams
        - project_score: Average project marks
        - attendance_percentage: Attendance percentage
        - overall_performance: Overall grade/status
    """
    PERFORMANCE_CHOICES = (
        ('excellent', 'Excellent (90-100)'),
        ('good', 'Good (80-89)'),
        ('average', 'Average (70-79)'),
        ('pass', 'Pass (60-69)'),
        ('fail', 'Fail (<60)'),
    )
    
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='performance_report'
    )
    average_exam_score = models.FloatField(default=0.0)
    project_score = models.FloatField(default=0.0)
    attendance_percentage = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    overall_performance = models.CharField(
        max_length=20,
        choices=PERFORMANCE_CHOICES,
        default='pass'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_score']
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.overall_performance}"
    
    def calculate_overall_score(self):
        """Calculate overall score from exam, project, and attendance."""
        # Weighted: Exams 60%, Projects 25%, Attendance 15%
        overall = (
            self.average_exam_score * 0.60 +
            self.project_score * 0.25 +
            self.attendance_percentage * 0.15
        )
        return overall
