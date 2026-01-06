import os
import sys
import pathlib
import django
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','exam_system.settings')
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
from apps.accounts.models import StudentProfile
User = get_user_model()

client = Client()
# Clean up test user if exists
User.objects.filter(username='reg_student').delete()

resp = client.post('/accounts/register/student/', data={
    'email': 'reg_student@example.com',
    'first_name': 'Reg',
    'last_name': 'Student',
    'password1': 'passw0rd123',
    'password2': 'passw0rd123',
    'department': 'BCA'
})
print('redirect status (should be 302):', resp.status_code)
user = User.objects.filter(email='reg_student@example.com').first()
print('user created:', bool(user))
if user:
    sp = StudentProfile.objects.filter(user=user).first()
    print('student profile exists:', bool(sp))
    print('department saved:', sp.department if sp else None)