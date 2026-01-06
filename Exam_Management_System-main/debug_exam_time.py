import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from apps.exams.models import ExamSchedule
from django.utils import timezone

schedules = ExamSchedule.objects.all()
now = timezone.now()

for schedule in schedules:
    exam_start = timezone.make_aware(
        timezone.datetime.combine(schedule.scheduled_date, schedule.start_time)
    )
    exam_end = timezone.make_aware(
        timezone.datetime.combine(schedule.scheduled_date, schedule.end_time)
    )
    
    print(f'\nSchedule ID: {schedule.id}')
    print(f'  Scheduled Date: {schedule.scheduled_date}')
    print(f'  Start Time: {schedule.start_time}')
    print(f'  End Time: {schedule.end_time}')
    print(f'  Current Time: {now}')
    print(f'  Exam Start: {exam_start}')
    print(f'  Exam End: {exam_end}')
    print(f'  is_exam_time(): {schedule.is_exam_time()}')
    print(f'  Now vs Start: {now} >= {exam_start} ? {now >= exam_start}')
    print(f'  Now vs End: {now} <= {exam_end} ? {now <= exam_end}')
