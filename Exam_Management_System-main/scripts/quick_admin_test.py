import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
django.setup()

from types import SimpleNamespace
from apps.ai_assistant.utils import get_local_ai_response

# Create a fake session object with a user who is staff
fake_user = SimpleNamespace(is_staff=True, is_superuser=False)
fake_session = SimpleNamespace(user=fake_user)

questions = [
    'how do i create an exam?',
    'how do i import students?',
    'how do i export reports?',
    'how do i update attendance for a class?'
]

for q in questions:
    print('Q:', q)
    print(get_local_ai_response(q, fake_session))
    print('-' * 50)
