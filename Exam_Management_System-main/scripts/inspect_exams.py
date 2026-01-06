import os
import sys
import django

# Ensure project root (parent directory) is on sys.path so Django settings can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from apps.exams.models import ExamSchedule
from apps.accounts.models import StudentProfile
from django.utils import timezone

now = timezone.now().date()
print('Today:', now)

schedules = ExamSchedule.objects.select_related('question_paper__subject').all()
print('Total schedules:', schedules.count())

for s in schedules:
    students = list(s.assigned_students.all())
    print('Schedule ID:', s.id, 'Date:', s.scheduled_date, 'Start:', s.start_time, 'End:', s.end_time, 'Subject:', s.question_paper.subject.name, 'Assigned count:', len(students))
    if students:
        for stu in students[:5]:
            print('  - Student:', stu.id, stu.enrollment_number, stu.department, stu.semester)

# Also list upcoming schedules
upcoming = schedules.filter(scheduled_date__gte=now).order_by('scheduled_date')
print('\nUpcoming schedules:', upcoming.count())
for s in upcoming:
    print('  ID:', s.id, 'Date:', s.scheduled_date, 'Subject:', s.question_paper.subject.name)
