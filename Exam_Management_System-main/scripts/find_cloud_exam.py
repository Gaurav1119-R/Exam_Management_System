import os
import sys
import django

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.utils import timezone
from apps.exams.models import ExamSchedule, QuestionPaper

now = timezone.now()

papers = QuestionPaper.objects.filter(title__icontains='cloud')
print('Found papers with "cloud" in title:', papers.count())
for p in papers:
    print('\nPaper:', p.id, p.title, 'Subject:', p.subject.name)
    schedules = ExamSchedule.objects.filter(question_paper=p)
    print('  Schedules for this paper:', schedules.count())
    for s in schedules:
        students = list(s.assigned_students.all())
        print('   Schedule ID:', s.id, 'Date:', s.scheduled_date, 'Start:', s.start_time, 'End:', s.end_time, 'Status:', s.status, 'Assigned:', len(students))
        if students:
            for stu in students:
                print('     - Student:', stu.id, stu.enrollment_number, stu.user.username)
        # show whether schedule is upcoming/ongoing according to our dashboard logic
        try:
            start_dt = timezone.make_aware(timezone.datetime.combine(s.scheduled_date, s.start_time))
            end_dt = timezone.make_aware(timezone.datetime.combine(s.scheduled_date, s.end_time))
            is_upcoming = end_dt >= now or start_dt >= now
            print('     Now:', now, 'start_dt:', start_dt, 'end_dt:', end_dt, 'is_upcoming_by_logic:', is_upcoming)
        except Exception as e:
            print('     Could not compute datetimes:', e)

if not papers.exists():
    print('\nNo paper with "cloud" found.')
else:
    print('\nSearch complete.')