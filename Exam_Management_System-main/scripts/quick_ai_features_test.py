import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
django.setup()

from apps.ai_assistant import services
from types import SimpleNamespace

fake_user = SimpleNamespace(is_staff=False)
from apps.ai_assistant.models import ChatSession
# create a minimal fake session object (without DB persistence) for service calls
fake_session = SimpleNamespace(user=fake_user)

print('1) Generate Questions (fallback)')
print(services.generate_questions('Math', 'easy', 3, use_openai=False))
print('-'*40)

print('2) Predict Results (mock)')
print(services.predict_results(session=None))
print('-'*40)

print('3) Analyze Weak Areas (mock)')
print(services.analyze_weak_areas(session=None))
print('-'*40)

print('4) Generate Practice Test')
print(services.generate_practice_test(fake_session, ['Algebra', 'Geometry'], num_questions=5, use_openai=False))
print('-'*40)

print('5) Chat tutor wrapper (using simple lambda)')
print(services.chat_tutor_response(lambda m, s: 'echo: '+m, 'How to study?', fake_session))
