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
    print(f'  Question Paper ID: {schedule.question_paper.id if schedule.question_paper else "None"}')
    if schedule.question_paper:
        paper = schedule.question_paper
        print(f'  Paper Title: {paper.title}')
        
        # Try different ways to access questions
        print(f'  Method 1 - .questions.all(): {paper.questions.all().count()}')
        print(f'  Method 2 - .questions.count(): {paper.questions.count()}')
        
        # List the questions
        for q in paper.questions.all():
            print(f'    Q{q.id}: {q.question_text[:40]}...')
