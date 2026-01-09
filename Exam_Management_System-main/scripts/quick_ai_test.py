import os
import django
import sys

# Ensure project root is on sys.path so `exam_system` imports correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()
from apps.ai_assistant.utils import get_local_ai_response, get_ai_response

questions = [
    'how do i prepare ?',
    'what are my scores?',
    'how to use the dashboard?',
    'when is my next exam?'
]

for q in questions:
    print('Q:', q)
    try:
        print('Local response:')
        print(get_local_ai_response(q, None))
    except Exception as e:
        print('Local error:', e)
    try:
        print('get_ai_response() (may use OpenAI if API key present):')
        print(get_ai_response(q, None))
    except Exception as e:
        print('get_ai_response error:', e)
    print('-' * 50)
