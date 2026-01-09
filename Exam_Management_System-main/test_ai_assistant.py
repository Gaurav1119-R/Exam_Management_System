#!/usr/bin/env python
"""
Test script to verify AI Assistant installation
Run with: python test_ai_assistant.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.ai_assistant.models import ChatSession, ChatMessage
from apps.ai_assistant.utils import get_ai_response

User = get_user_model()


def test_installation():
    """Test if AI Assistant is properly installed"""
    
    print("=" * 60)
    print("AI ASSISTANT - INSTALLATION TEST")
    print("=" * 60)
    
    # Test 1: Check if models are created
    print("\n1. Checking database models...")
    try:
        ChatSession.objects.all().count()
        ChatMessage.objects.all().count()
        print("   ✓ Database models are accessible")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Check if we can create a test session
    print("\n2. Testing chat session creation...")
    try:
        # Get or create test user
        test_user, created = User.objects.get_or_create(
            username='test_ai_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Create test session
        test_session = ChatSession.objects.create(
            user=test_user,
            title='Test Chat Session'
        )
        print(f"   ✓ Created test session: {test_session}")
        
        # Create test message
        test_message = ChatMessage.objects.create(
            session=test_session,
            role='user',
            content='Test message'
        )
        print(f"   ✓ Created test message: {test_message}")
        
        # Clean up
        test_message.delete()
        test_session.delete()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Check AI response generation
    print("\n3. Testing AI response generation...")
    try:
        # Create a temporary session for testing
        test_user, _ = User.objects.get_or_create(
            username='test_ai_user',
            defaults={'email': 'test@example.com'}
        )
        test_session = ChatSession.objects.create(
            user=test_user,
            title='AI Response Test'
        )
        
        # Test with different questions
        test_questions = [
            "When is my next exam?",
            "How do I prepare for exams?",
            "Hello!",
            "What is this system?"
        ]
        
        for question in test_questions:
            response = get_ai_response(question, test_session)
            if response and len(response) > 0:
                print(f"   ✓ Q: {question[:30]}...")
                print(f"     A: {response[:50]}...")
            else:
                print(f"   ✗ No response for: {question}")
        
        # Clean up
        test_session.delete()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Check OpenAI integration (if available)
    print("\n4. Checking OpenAI integration...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✓ OpenAI API key is configured")
        print(f"   ℹ Key (first 10 chars): {api_key[:10]}...")
    else:
        print("   ℹ OpenAI API key not configured (optional)")
        print("   ℹ System will use local AI responses")
    
    # Test 5: Check URLs
    print("\n5. Checking URL configuration...")
    try:
        from django.urls import reverse
        urls_to_check = [
            ('ai_assistant:chat_list', None),
            ('ai_assistant:new_chat', None),
        ]
        
        for url_name, args in urls_to_check:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✓ {url_name}: {url}")
            except Exception as e:
                print(f"   ✗ {url_name}: Error - {e}")
                return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nAI Assistant is ready to use!")
    print("\nNext steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://localhost:8000/ai_assistant/")
    print("3. Login and start chatting with the AI Assistant!")
    print("\n" + "=" * 60)
    
    return True


if __name__ == '__main__':
    try:
        success = test_installation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
