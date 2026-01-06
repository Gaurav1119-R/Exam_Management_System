import os
import sys
import django
from django.utils import timezone
from datetime import timedelta, datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from apps.exams.models import QuestionPaper, ExamSchedule
from apps.accounts.models import StudentProfile

now = timezone.now()
# schedule starts in 2 minutes by default
start_dt = now + timedelta(minutes=2)
end_dt = start_dt + timedelta(minutes=60)

paper = QuestionPaper.objects.filter(title__icontains='cloud').first()
if not paper:
    print('No cloud paper found')
    sys.exit(1)

schedule = ExamSchedule.objects.create(
    question_paper=paper,
    scheduled_date=start_dt.date(),
    start_time=start_dt.time().replace(microsecond=0),
    end_time=end_dt.time().replace(microsecond=0),
    status='published'
)

students = StudentProfile.objects.all()
schedule.assigned_students.set(students)

print('Created schedule:', schedule.id, 'for paper:', paper.id, paper.title)
print('Scheduled date:', schedule.scheduled_date, 'start:', schedule.start_time, 'end:', schedule.end_time)
print('Assigned students count:', students.count())
