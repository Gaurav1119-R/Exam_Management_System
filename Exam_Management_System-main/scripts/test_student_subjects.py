import os
import sys
import pathlib
import django
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','exam_system.settings')
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
from apps.exams.models import Subject, Department
from apps.accounts.models import StudentProfile
User = get_user_model()

# Ensure departments/subjects exist
if not Department.objects.exists():
    from setup_departments_subjects import setup_departments_and_subjects
    setup_departments_and_subjects()

# Create test student
user, created = User.objects.get_or_create(username='subj_student', defaults={'email':'subj_student@example.com','first_name':'Subj','last_name':'Student','role':'student'})
if created:
    user.set_password('testpass123')
    user.save()

sp, _ = StudentProfile.objects.get_or_create(user=user, defaults={'enrollment_number':'SS1001','department':'BCA','semester':1})
client = Client()
client.login(username='subj_student', password='testpass123')
resp = client.get('/exams/student/subjects/')
print('status:', resp.status_code)
print('contains BCA-AI-ML:', 'BCA-AI-ML' in resp.content.decode())
