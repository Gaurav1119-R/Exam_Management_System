# Model Reference Guide

## User & Authentication Models

### `User` (accounts/models.py)
```python
class User(AbstractUser):
    """Custom user with role-based system"""
    
    Fields:
        - username: str (unique)
        - email: str (unique)
        - first_name, last_name: str
        - role: str (choices: 'admin', 'student')
        - phone_number: str (optional)
        - is_active: bool (inherited)
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Properties:
        - is_admin_user: bool → (role == 'admin')
        - is_student_user: bool → (role == 'student')
    
    Reverse Relations:
        - student_profile: StudentProfile (1:1)
        - created_questions: Question (1:N)
        - created_papers: QuestionPaper (1:N)
        - marked_attendances: Attendance (1:N)
```

### `StudentProfile` (accounts/models.py)
```python
class StudentProfile(models.Model):
    """Extended student information (1:1 with User)"""
    
    Fields:
        - user: ForeignKey(User) → unique
        - enrollment_number: str (unique, indexed)
        - department: str
        - semester: int (1-8)
        - profile_picture: ImageField (optional)
        - date_of_birth: DateField (optional)
        - address: str (optional)
        - is_active: bool (default: True)
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Reverse Relations:
        - exam_schedules: ExamSchedule (M:N)
        - attendances: Attendance (1:N)
        - exam_responses: StudentExamResponse (1:N)
        - exam_results: StudentExamResult (1:N)
        - project_reports: ProjectReport (1:N)
        - performance_report: StudentReport (1:1)
        - attendance_report: AttendanceReport (1:1)
```

---

## Exam Management Models

### `Subject` (exams/models.py)
```python
class Subject(models.Model):
    """Academic subject/course"""
    
    Fields:
        - code: str (unique, indexed)
        - name: str
        - description: str (optional)
        - credits: int (1-4)
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Reverse Relations:
        - questions: Question (1:N)
        - question_papers: QuestionPaper (1:N)
    
    Methods:
        - __str__(): returns "CODE - NAME"
```

### `Question` (exams/models.py)
```python
class Question(models.Model):
    """Individual question (MCQ or Descriptive)"""
    
    Fields:
        - subject: ForeignKey(Subject)
        - question_text: str (TextField)
        - question_type: str (choices: 'mcq', 'descriptive')
        - marks: int (min: 1)
        
        # MCQ specific
        - option_a, option_b, option_c, option_d: str (optional)
        - correct_answer: str (choices: 'a', 'b', 'c', 'd')
        
        - created_by: ForeignKey(User) → can be null
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Constraints:
        - For MCQ: All 4 options + correct_answer required
        - For Descriptive: Options ignored
    
    Methods:
        - is_valid_mcq(): bool → checks MCQ completeness
    
    Reverse Relations:
        - papers: QuestionPaper (M:N)
        - student_responses: StudentExamResponse (1:N)
```

### `QuestionPaper` (exams/models.py)
```python
class QuestionPaper(models.Model):
    """Collection of questions for an exam"""
    
    Fields:
        - title: str
        - subject: ForeignKey(Subject)
        - questions: ManyToManyField(Question)
        - total_marks: int (calculated)
        - duration_minutes: int (15-480 min)
        - passing_marks: int (0-100)
        - instructions: str (optional)
        - created_by: ForeignKey(User) → can be null
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Methods:
        - get_total_marks(): int → sum of question marks
    
    Reverse Relations:
        - schedules: ExamSchedule (1:N)
```

### `ExamSchedule` (exams/models.py)
```python
class ExamSchedule(models.Model):
    """Scheduled exam with assigned students"""
    
    Fields:
        - question_paper: ForeignKey(QuestionPaper)
        - scheduled_date: Date (indexed)
        - start_time: Time
        - end_time: Time
        - assigned_students: ManyToManyField(StudentProfile)
        - status: str (choices: 'draft', 'published', 'ongoing', 'completed')
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Methods:
        - is_exam_time(): bool → check if now is within start-end time
    
    Reverse Relations:
        - student_responses: StudentExamResponse (1:N)
        - results: StudentExamResult (1:N)
        - attendances: Attendance (1:N)
    
    Unique Constraint:
        - (question_paper, scheduled_date, start_time) [implicit]
```

### `StudentExamResponse` (exams/models.py)
```python
class StudentExamResponse(models.Model):
    """Individual student answer to a question"""
    
    Fields:
        - exam_schedule: ForeignKey(ExamSchedule)
        - student: ForeignKey(StudentProfile)
        - question: ForeignKey(Question)
        - student_answer: str (MCQ: a/b/c/d, Descriptive: text)
        - marks_obtained: int (optional, null if not graded)
        - answered_at: datetime (auto)
    
    Constraints:
        - Unique together: (exam_schedule, student, question)
    
    Usage:
        - For MCQ: Compare student_answer with question.correct_answer
        - For Descriptive: Admin manually sets marks_obtained
    
    Ordering:
        - By -answered_at (newest first)
```

### `StudentExamResult` (exams/models.py)
```python
class StudentExamResult(models.Model):
    """Aggregated result for one student's exam"""
    
    Fields:
        - exam_schedule: ForeignKey(ExamSchedule)
        - student: ForeignKey(StudentProfile)
        - total_marks: int
        - marks_obtained: int
        - percentage: float (calculated)
        - status: str (choices: 'passed', 'failed', 'pending')
        - graded_at: datetime
    
    Constraints:
        - Unique together: (exam_schedule, student)
    
    Calculation:
        - percentage = (marks_obtained / total_marks) * 100
        - status = 'passed' if percentage >= passing_marks else 'failed'
```

---

## Attendance Models

### `Attendance` (attendance/models.py)
```python
class Attendance(models.Model):
    """Attendance record for one student in one exam"""
    
    Fields:
        - exam_schedule: ForeignKey(ExamSchedule)
        - student: ForeignKey(StudentProfile)
        - attended: bool (default: False)
        - check_in_time: datetime (optional)
        - check_out_time: datetime (optional)
        - marked_by: ForeignKey(User) → can be null
        - marked_at: datetime (auto-updated)
        - notes: str (optional)
    
    Constraints:
        - Unique together: (exam_schedule, student)
    
    Reverse Relations:
        - marked_by is ForeignKey → User.marked_attendances (1:N)
```

### `AttendanceReport` (attendance/models.py)
```python
class AttendanceReport(models.Model):
    """Aggregated attendance statistics for student"""
    
    Fields:
        - student: OneToOneField(StudentProfile)
        - total_exams: int (sum of assigned exams)
        - exams_attended: int (count of attended exams)
        - attendance_percentage: float (calculated)
        - updated_at: datetime (auto)
    
    Methods:
        - calculate_percentage(): float → (exams_attended / total_exams) * 100
```

---

## Reports Models

### `ProjectReport` (reports/models.py)
```python
class ProjectReport(models.Model):
    """Project submission by student"""
    
    Fields:
        - student: ForeignKey(StudentProfile)
        - title: str
        - description: str (TextField)
        - file: FileField (only: pdf, doc, docx, zip, rar)
        - submission_date: datetime (auto)
        - due_date: Date
        - marks_obtained: int (optional, null if not graded)
        - total_marks: int (default: 100)
        - status: str (choices: 'pending', 'submitted', 'graded', 'late')
        - feedback: str (optional)
        - created_at: datetime (auto)
        - updated_at: datetime (auto)
    
    Methods:
        - is_late(): bool → submission_date > due_date
    
    Constraints:
        - File validation: extension check in model
```

### `StudentReport` (reports/models.py)
```python
class StudentReport(models.Model):
    """Overall performance summary for student"""
    
    Fields:
        - student: OneToOneField(StudentProfile)
        - average_exam_score: float (default: 0.0)
        - project_score: float (default: 0.0)
        - attendance_percentage: float (default: 0.0)
        - overall_score: float (calculated)
        - overall_performance: str (choices: 'excellent', 'good', 'average', 'pass', 'fail')
        - updated_at: datetime (auto)
    
    Methods:
        - calculate_overall_score(): float
            → (exam_score * 0.6) + (project_score * 0.25) + (attendance * 0.15)
    
    Performance Ranges:
        - excellent: 90-100
        - good: 80-89
        - average: 70-79
        - pass: 60-69
        - fail: <60
```

---

## Query Patterns & Examples

### Get admin user with question count
```python
admin_user = User.objects.filter(is_admin_user=True).first()
question_count = admin_user.created_questions.count()
```

### Get student with enrolled exams
```python
student = StudentProfile.objects.select_related('user').prefetch_related('exam_schedules').get(enrollment_number='2024001')
upcoming_exams = student.exam_schedules.filter(status='published')
```

### Get exam schedule with all details
```python
schedule = ExamSchedule.objects.select_related('question_paper__subject').prefetch_related('assigned_students').get(pk=1)
total_questions = schedule.question_paper.questions.count()
assigned_count = schedule.assigned_students.count()
```

### Get student exam response details
```python
responses = StudentExamResponse.objects.filter(
    exam_schedule=schedule,
    student=student
).select_related('question')

for response in responses:
    if response.question.question_type == 'mcq':
        is_correct = response.student_answer == response.question.correct_answer
```

### Get student performance
```python
from django.db.models import Avg, Count

results = StudentExamResult.objects.filter(student=student)
avg_percentage = results.aggregate(Avg('percentage'))['percentage__avg']
passed_count = results.filter(status='passed').count()
```

---

## Common Field Validators & Constraints

### Integer Ranges
```python
marks = models.IntegerField(validators=[MinValueValidator(1)])
semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
duration = models.IntegerField(validators=[MinValueValidator(15), MaxValueValidator(480)])
```

### File Uploads
```python
file = models.FileField(
    upload_to='project_reports/',
    validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
)
```

### Unique Fields
```python
enrollment_number = models.CharField(max_length=50, unique=True)
# Also create index: db_index=True
```

### Choice Fields
```python
status = models.CharField(
    max_length=20,
    choices=[('pending', 'Pending'), ('graded', 'Graded')],
    default='pending'
)
```

---

## Migration Commands

```bash
# Create migrations from model changes
python manage.py makemigrations apps.exams

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations apps.exams

# Rollback migrations
python manage.py migrate apps.exams 0001  # Go to specific migration

# Create empty migration for data changes
python manage.py makemigrations --empty apps.exams --name add_field_to_model
```

---

## Model Management via Django Shell

```python
# Access Django shell
python manage.py shell

# Create subject
subject = Subject.objects.create(code='CSC101', name='Python', credits=3)

# Create question
question = Question.objects.create(
    subject=subject,
    question_text='What is Python?',
    question_type='mcq',
    marks=5,
    option_a='Language',
    option_b='Tool',
    option_c='Framework',
    option_d='Library',
    correct_answer='a'
)

# Create paper
paper = QuestionPaper.objects.create(
    title='Midterm',
    subject=subject,
    total_marks=50,
    duration_minutes=60,
    passing_marks=25
)
paper.questions.add(question)

# Bulk operations
StudentProfile.objects.filter(department='CS').update(is_active=False)

# Count and stats
total_students = StudentProfile.objects.count()
students_in_cs = StudentProfile.objects.filter(department='CS').count()
```

This guide serves as a quick reference for understanding the data model and common operations.
