import os
import sys
import pathlib
import django
# Ensure project root is on sys.path so Django settings can be imported
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','exam_system.settings')
django.setup()
from django.contrib.auth import get_user_model
from apps.accounts.models import StudentProfile
from django.test import Client
User=get_user_model()
user, created = User.objects.get_or_create(username='test_student', defaults={'email':'test_student@example.com','first_name':'Test','last_name':'Student','role':'student'})
if created:
    user.set_password('testpass123')
    user.save()
sp, sc = StudentProfile.objects.get_or_create(user=user, defaults={'enrollment_number':'TS1001','department':'BCA','semester':1})
if not sc:
    sp.department='BCA'
    sp.save()
client=Client()
logged = client.login(username='test_student', password='testpass123')
print('logged_in:', logged)
resp = client.get('/accounts/profile/update/')
print('status:', resp.status_code)
content = resp.content.decode()
print('has subject-select-container:', 'id="subject-select-container"' in content)
print('department select ids present:', 'id="department-select"' in content or 'id="id_department"' in content)

# --- Admin page checks ---
admin_user, admin_created = User.objects.get_or_create(username='test_admin', defaults={'email':'test_admin@example.com','first_name':'Admin','last_name':'User','role':'admin'})
if admin_created:
    admin_user.set_password('adminpass123')
    admin_user.save()
client.logout()
logged_admin = client.login(username='test_admin', password='adminpass123')
print('admin logged_in:', logged_admin)
admin_resp = client.get('/exams/admin/papers/create/')
print('admin page status:', admin_resp.status_code)
admin_html = admin_resp.content.decode()
print('admin has id_subject:', 'id="id_subject"' in admin_html)
print('admin has department select:', 'id="id_department"' in admin_html or 'id="department-select"' in admin_html)
