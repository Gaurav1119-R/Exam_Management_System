from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class ExamHistoryViewTests(TestCase):
    """Tests for the student exam history view."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='student1', password='testpass', role='student'
        )
        # Do not explicitly create StudentProfile; view will create it when needed
        self.client.login(username='student1', password='testpass')

    def test_history_renders_with_empty_results(self):
        """When there are no exam results, the page should render and show a fallback message."""
        url = reverse('exams:student:exam_history')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'No exam history available.')

    def test_sidebar_hidden_on_page(self):
        """The page should include page-specific CSS that hides the left sidebar."""
        url = reverse('exams:student:exam_history')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '.sidebar-gradient { display: none !important; }')


class AdminDashboardTests(TestCase):
    """Tests for the admin dashboard view and counts endpoint."""

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin1', password='testpass', role='admin')
        self.client.login(username='admin1', password='testpass')

    def test_dashboard_renders_and_contains_links(self):
        url = reverse('exams:admin:dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Ensure links to management pages and profile exist
        self.assertContains(resp, reverse('exams:admin:subject_list'))
        self.assertContains(resp, reverse('exams:admin:subject_create'))
        self.assertContains(resp, reverse('exams:admin:schedule_list'))
        self.assertContains(resp, reverse('exams:admin:schedule_create'))
        self.assertContains(resp, reverse('profile'))
        # Admin profile page should include email and role when visited
        resp2 = self.client.get(reverse('profile'))
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, self.admin.email)
        self.assertContains(resp2, 'Admin')

    def test_counts_endpoint_returns_json(self):
        url = reverse('exams:admin:dashboard_counts')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Keys should be present and integer values
        for k in ['total_subjects', 'total_questions', 'total_papers', 'total_schedules']:
            self.assertIn(k, data)
            self.assertIsInstance(data[k], int)

    def test_counts_endpoint_forbidden_for_non_admin(self):
        # create a regular user and ensure access denied
        User = get_user_model()
        user = User.objects.create_user(username='user1', password='testpass', role='student')
        self.client.login(username='user1', password='testpass')
        url = reverse('exams:admin:dashboard_counts')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

