from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage


class ChatSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.session = ChatSession.objects.create(user=self.user, title='Test Chat')

    def test_chat_session_creation(self):
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.title, 'Test Chat')

    def test_chat_message_creation(self):
        message = ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Hello AI'
        )
        self.assertEqual(message.session, self.session)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello AI')


class ChatViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.session = ChatSession.objects.create(user=self.user, title='Test Chat')

    def test_chat_view_requires_login(self):
        response = self.client.get(f'/ai_assistant/chat/{self.session.id}/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_chat_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(f'/ai_assistant/chat/{self.session.id}/')
        self.assertEqual(response.status_code, 200)
