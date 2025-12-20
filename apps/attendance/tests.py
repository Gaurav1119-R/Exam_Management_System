from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, time, timedelta

from apps.accounts.models import User, StudentProfile
from apps.attendance.models import Attendance, AttendanceReport
from apps.exams.models import Subject, QuestionPaper, ExamSchedule


class AttendanceModelTests(TestCase):
    def setUp(self):
        # Create a student user and profile
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='password123',
            role='student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            enrollment_number='S2025001',
            department='CS',
            semester=1,
        )

    def test_attendance_report_percentage_zero_total(self):
        report = AttendanceReport.objects.create(
            student=self.student_profile,
            total_exams=0,
            exams_attended=0,
            attendance_percentage=0.0,
        )
        self.assertEqual(report.calculate_percentage(), 0.0)

    def test_attendance_report_percentage_calculation(self):
        report = AttendanceReport.objects.create(
            student=self.student_profile,
            total_exams=10,
            exams_attended=7,
            attendance_percentage=0.0,
        )
        self.assertAlmostEqual(report.calculate_percentage(), 70.0)


class AttendanceExportViewTests(TestCase):
    def setUp(self):
        # Create users: student and admin (creator for papers)
        self.student_user = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='password123',
            role='student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            enrollment_number='S2025002',
            department='CS',
            semester=2,
        )

        self.admin_user = User.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='adminpass',
            role='admin'
        )

        # Create subject and paper
        self.subject = Subject.objects.create(code='TST101', name='Test Subject', credits=3)
        self.paper = QuestionPaper.objects.create(
            title='Test Paper',
            subject=self.subject,
            total_marks=100,
            duration_minutes=60,
            passing_marks=40,
            created_by=self.admin_user,
        )

        # Create exam schedules for different dates
        today = timezone.now().date()
        self.schedule_recent = ExamSchedule.objects.create(
            question_paper=self.paper,
            scheduled_date=today - timedelta(days=5),
            start_time=time(9, 0),
            end_time=time(11, 0),
            status='published',
        )
        self.schedule_old = ExamSchedule.objects.create(
            question_paper=self.paper,
            scheduled_date=today - timedelta(days=40),
            start_time=time(9, 0),
            end_time=time(11, 0),
            status='published',
        )

        # Assign student to schedules
        self.schedule_recent.assigned_students.add(self.student_profile)
        self.schedule_old.assigned_students.add(self.student_profile)

        # Create attendance records
        Attendance.objects.create(
            exam_schedule=self.schedule_recent,
            student=self.student_profile,
            attended=True,
            marked_by=self.admin_user,
        )
        Attendance.objects.create(
            exam_schedule=self.schedule_old,
            student=self.student_profile,
            attended=False,
            marked_by=self.admin_user,
        )

        # Client for requests
        self.client = Client()

    def test_export_all_attendance_csv(self):
        # Log in as student
        login = self.client.login(username='student2', password='password123')
        self.assertTrue(login)

        url = reverse('attendance:student_report_export')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        content = resp.content.decode('utf-8')
        # Header should be present
        self.assertIn('Date,Subject,Time,Status', content.replace('\r', ''))
        # Both records should be present
        self.assertIn(self.schedule_recent.scheduled_date.isoformat(), content)
        self.assertIn(self.schedule_old.scheduled_date.isoformat(), content)

    def test_export_last30_filter(self):
        login = self.client.login(username='student2', password='password123')
        self.assertTrue(login)

        url = reverse('attendance:student_report_export') + '?filter=last30'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Recent date should be present, old date should not
        self.assertIn(self.schedule_recent.scheduled_date.isoformat(), content)
        self.assertNotIn(self.schedule_old.scheduled_date.isoformat(), content)

    def test_student_attendance_report_view(self):
        # Use RequestFactory to call the view directly to avoid template signal
        # copying issues in some environments.
        from django.test import RequestFactory
        from apps.attendance.views import student_attendance_report

        factory = RequestFactory()
        request = factory.get(reverse('attendance:student_report'))
        request.user = self.student_user

        resp = student_attendance_report(request)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Ensure Back to Dashboard link is present
        self.assertIn(reverse('exams:student:dashboard'), content)

    def test_student_attendance_report_no_month_data(self):
        # New student with no attendance should see the 'No attendance trend' message
        from django.test import RequestFactory
        from apps.attendance.views import student_attendance_report

        user = User.objects.create_user(username='student3', email='s3@example.com', password='pw', role='student')
        StudentProfile.objects.create(user=user, enrollment_number='S2025003', department='CS', semester=1)

        factory = RequestFactory()
        request = factory.get(reverse('attendance:student_report'))
        request.user = user
        resp = student_attendance_report(request)
        content = resp.content.decode('utf-8')
        self.assertIn('No attendance trend data for the selected period.', content)
