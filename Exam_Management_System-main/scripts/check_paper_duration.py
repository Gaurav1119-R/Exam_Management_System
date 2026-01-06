import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
import django
django.setup()

from apps.exams.models import QuestionPaper
p = QuestionPaper.objects.filter(title__icontains='cloud').first()
if not p:
    print('No cloud paper')
else:
    print('Paper id', p.id, 'title:', p.title, 'duration_minutes:', p.duration_minutes)
    print('Total marks (get_total_marks):', p.get_total_marks())
