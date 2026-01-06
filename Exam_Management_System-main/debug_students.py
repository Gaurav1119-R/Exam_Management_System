import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import StudentProfile
from apps.exams.models import ExamSchedule

User = get_user_model()

# Check users
students = User.objects.filter(role='student')
print(f'Total student users: {students.count()}')

for student in students:
    print(f'\nStudent: {student.username} ({student.email})')
    try:
        profile = StudentProfile.objects.get(user=student)
        exams = profile.exam_schedules.all()
        print(f'  Exam schedules: {exams.count()}')
        for exam in exams:
            print(f'    - Schedule ID: {exam.id}, Paper: {exam.question_paper}')
    except StudentProfile.DoesNotExist:
        print('  No profile found')
