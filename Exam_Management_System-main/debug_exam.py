import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from apps.exams.models import ExamSchedule, QuestionPaper, Question

# Check schedules
schedules = ExamSchedule.objects.all()
print(f'Total exam schedules: {schedules.count()}')

for schedule in schedules:
    print(f'\nSchedule ID: {schedule.id}')
    print(f'  Question Paper: {schedule.question_paper}')
    if schedule.question_paper:
        questions = schedule.question_paper.questions.all()
        print(f'  Questions in paper: {questions.count()}')
        for q in questions:
            print(f'    - Q{q.id}: {q.question_text[:50]}... (Type: {q.question_type})')
    else:
        print('  ERROR: No question paper assigned!')
