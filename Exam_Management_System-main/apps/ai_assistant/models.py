from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """Store chat sessions between users and AI assistant"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, default="New Chat")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Store individual messages in a chat session"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class Prediction(models.Model):
    """Store simple ML predictions for a student/exam combination"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='predictions')
    predicted_score = models.FloatField()
    confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.session.id}: {self.predicted_score} ({self.confidence})"


class PracticeTest(models.Model):
    """A generated practice test saved for a user session"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='practice_tests')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PracticeTest {self.title} ({self.session.id})"


class WeakArea(models.Model):
    """Detected weak areas for a user (simple tag + score)"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='weak_areas')
    topic = models.CharField(max_length=255)
    severity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.topic} (sev {self.severity})"
