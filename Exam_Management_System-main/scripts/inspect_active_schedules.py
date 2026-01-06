import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
import django
from django.utils import timezone
from datetime import datetime

django.setup()
from apps.exams.models import ExamSchedule

now = timezone.now()
print('Now:', now)
for s in ExamSchedule.objects.all():
    paper = s.question_paper
    print('Schedule', s.id, 'Paper', paper.id, paper.title, 'duration_minutes', paper.duration_minutes, 'date', s.scheduled_date, 'start', s.start_time, 'end', s.end_time, 'status', s.status, 'assigned_count', s.assigned_students.count())
    try:
        start_dt = timezone.make_aware(datetime.combine(s.scheduled_date, s.start_time))
        end_dt = timezone.make_aware(datetime.combine(s.scheduled_date, s.end_time))
        print('  start_dt', start_dt, 'end_dt', end_dt, 'is ongoing', start_dt<=now<=end_dt)
    except Exception as e:
        print('  datetime comp failed', e)
