from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
from .models import ChatSession, ChatMessage
from .forms import ChatMessageForm
from .utils import get_ai_response
from . import services


@login_required
def chat_view(request, session_id=None):
    """Main chat interface"""
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        # Create new session
        session = ChatSession.objects.create(
            user=request.user,
            title="Exam Assistant Chat"
        )
        return redirect('ai_assistant:chat', session_id=session.id)

    messages = session.messages.all()
    form = ChatMessageForm()
    user_sessions = request.user.chat_sessions.all()[:10]

    context = {
        'session': session,
        'messages': messages,
        'form': form,
        'user_sessions': user_sessions,
    }

    return render(request, 'ai_assistant/chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request, session_id):
    """Handle message sending via AJAX"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        # Get AI response
        ai_response_text = get_ai_response(user_message, session)

        # Save AI response
        ai_msg = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=ai_response_text
        )

        return JsonResponse({
            'user_message': user_msg.content,
            'ai_response': ai_msg.content,
            'success': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def new_chat(request):
    """Create a new chat session"""
    session = ChatSession.objects.create(
        user=request.user,
        title="Exam Assistant Chat"
    )
    return redirect('ai_assistant:chat', session_id=session.id)


@login_required
@require_http_methods(["POST"])
def delete_session(request, session_id):
    """Delete a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return redirect('ai_assistant:chat_list')


@login_required
def chat_list(request):
    """List all chat sessions for the user"""
    sessions = request.user.chat_sessions.all()
    context = {'sessions': sessions}
    return render(request, 'ai_assistant/chat_list.html', context)


@login_required
@require_http_methods(["POST"])
def generate_questions_view(request, session_id):
    """Generate questions for a subject via AI service"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    try:
        data = json.loads(request.body)
        subject = data.get('subject', 'General')
        difficulty = data.get('difficulty', 'medium')
        count = int(data.get('count', 5))
        questions = services.generate_questions(subject, difficulty, count)
        return JsonResponse({'questions': questions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def predict_results_view(request, session_id):
    """Return a mock ML prediction for a student/exam"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    try:
        res = services.predict_results(session=session)
        return JsonResponse({'prediction': res})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def generate_practice_view(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    try:
        data = json.loads(request.body)
        topics = data.get('topics', [])
        num_questions = int(data.get('num_questions', 10))
        test = services.generate_practice_test(session, topics, num_questions)
        return JsonResponse({'practice_test': test})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
