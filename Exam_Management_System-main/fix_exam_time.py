import os
import django
from datetime import datetime, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from apps.exams.models import ExamSchedule
from django.utils import timezone

# Get current time
now = timezone.now()
current_time = now.time()
current_date = now.date()

# Create exam times - set start to 1 hour ago, end to 1 hour from now
start_time = time(current_time.hour - 1 if current_time.hour > 0 else 23, current_time.minute, 0)
end_time = time((current_time.hour + 1) % 24, current_time.minute, 0)

print(f'Current Date: {current_date}')
print(f'Current Time: {current_time}')
print(f'Setting exam window:')
print(f'  Start: {start_time}')
print(f'  End: {end_time}')

# Update all schedules to have current time in their exam window
ExamSchedule.objects.all().update(
    scheduled_date=current_date,
    start_time=start_time,
    end_time=end_time
)

print(f'\nUpdated {ExamSchedule.objects.count()} exam schedules')

# Verify
for schedule in ExamSchedule.objects.all():
    print(f'\nSchedule {schedule.id}:')
    print(f'  Date: {schedule.scheduled_date}')
    print(f'  Start: {schedule.start_time}')
    print(f'  End: {schedule.end_time}')
    print(f'  is_exam_time(): {schedule.is_exam_time()}')
