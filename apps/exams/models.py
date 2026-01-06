"""
Models for exams, questions, and scheduling.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User, StudentProfile


class Subject(models.Model):
    """
    Subject model - represents academic subjects/courses.
    
    Fields:
        - code: Unique subject code (e.g., CSC101)
        - name: Subject name
        - description: Subject description
        - credits: Academic credits
        - created_at: Creation timestamp
    """
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        indexes = [models.Index(fields=['code'])]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Question(models.Model):
    """
    Question model - stores individual questions.
    
    Fields:
        - subject: Foreign key to Subject
        - question_text: The question content
        - question_type: MCQ or Descriptive
        - marks: Points assigned to question
        - option_a, option_b, option_c, option_d: MCQ options
        - correct_answer: Correct option for MCQ
        - created_by: Admin user who created question
    """
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('descriptive', 'Descriptive'),
    )
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField(validators=[MinValueValidator(1)])
    
    # MCQ specific fields
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')],
        blank=True
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'question_type']),
        ]
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}... ({self.get_question_type_display()})"
    
    def is_valid_mcq(self):
        """Check if MCQ question has all required fields."""
        if self.question_type == 'mcq':
            return all([self.option_a, self.option_b, self.option_c, 
                       self.option_d, self.correct_answer])
        return True


class QuestionPaper(models.Model):
    """
    QuestionPaper model - represents an exam question paper.
    
    Fields:
        - title: Paper title
        - subject: Foreign key to Subject
        - questions: Many-to-many with Question
        - total_marks: Sum of all question marks
        - duration_minutes: Exam duration in minutes
        - passing_marks: Minimum marks to pass
        - created_by: Admin who created paper
    """
    title = models.CharField(max_length=300)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='question_papers'
    )
    questions = models.ManyToManyField(Question, related_name='papers')
    total_marks = models.IntegerField(default=100)
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(480)]
    )
    passing_marks = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    instructions = models.TextField(blank=True, help_text="Exam instructions for students")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_papers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.subject.code} - {self.title}"
    
    def get_total_marks(self):
        """Calculate total marks from questions."""
        return self.questions.aggregate(models.Sum('marks'))['marks__sum'] or 0


class ExamSchedule(models.Model):
    """
    ExamSchedule model - schedules exams for students.
    
    Fields:
        - question_paper: Foreign key to QuestionPaper
        - scheduled_date: Date of exam
        - start_time: Start time of exam
        - end_time: End time of exam (calculated from duration)
        - assigned_students: Many-to-many with StudentProfile
        - status: Published/Draft/Completed
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    
    question_paper = models.ForeignKey(
        QuestionPaper,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    scheduled_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    assigned_students = models.ManyToManyField(
        StudentProfile,
        related_name='exam_schedules'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date', 'start_time']
        indexes = [
            models.Index(fields=['scheduled_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.question_paper.subject.code} - {self.scheduled_date}"
    
    def is_exam_time(self):
        """Check if current time is during exam."""
        now = timezone.now()
        exam_datetime_start = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.start_time)
        )
        exam_datetime_end = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.end_time)
        )
        return exam_datetime_start <= now <= exam_datetime_end


class StudentExamResponse(models.Model):
    """
    StudentExamResponse model - stores student answers for exams.
    
    Fields:
        - exam_schedule: Foreign key to ExamSchedule
        - student: Foreign key to StudentProfile
        - question: Foreign key to Question
        - student_answer: The answer provided by student
        - marks_obtained: Marks awarded (null if not graded)
        - answered_at: Timestamp of answer submission
    """
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='student_responses'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='exam_responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_responses'
    )
    student_answer = models.TextField()
    marks_obtained = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('exam_schedule', 'student', 'question')
        ordering = ['-answered_at']
        indexes = [
            models.Index(fields=['exam_schedule', 'student']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - Q{self.question.id}"


class StudentExamResult(models.Model):
    """
    StudentExamResult model - aggregated results for each exam.
    
    Fields:
        - exam_schedule: Foreign key to ExamSchedule
        - student: Foreign key to StudentProfile
        - total_marks: Total marks in exam
        - marks_obtained: Total marks obtained
        - percentage: Percentage score
        - status: Pass/Fail
        - graded_at: When result was finalized
    """
    STATUS_CHOICES = (
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('pending', 'Pending Grading'),
    )
    
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='results'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='exam_results'
    )
    total_marks = models.IntegerField()
    marks_obtained = models.IntegerField()
    percentage = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    graded_at = models.DateTimeField()
    
    class Meta:
        unique_together = ('exam_schedule', 'student')
        ordering = ['-graded_at']
        indexes = [
            models.Index(fields=['exam_schedule', 'student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.percentage}%"
