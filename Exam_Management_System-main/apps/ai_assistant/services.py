import os
import random
from typing import List, Dict, Optional

from .models import PracticeTest, Prediction, WeakArea, ChatSession


def _use_openai(prompt: str, max_tokens: int = 200) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return ''
    try:
        import openai
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'system', 'content': 'You are a helpful question generator.'},
                      {'role': 'user', 'content': prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print('OpenAI error in services._use_openai:', e)
        return ''


# 1) GPT Question Generation (stub)
def generate_questions(subject: str, difficulty: str = 'medium', count: int = 5, use_openai: bool = True) -> List[Dict]:
    """Generate a list of question dicts for a given subject and difficulty.

    If OpenAI API key is present and use_openai=True, call OpenAI; otherwise return simple templated questions.
    """
    prompt = f"Generate {count} {difficulty} questions for {subject} as a numbered list. Include correct answers." 
    if use_openai:
        res = _use_openai(prompt)
        if res:
            # Return raw text in a single item when OpenAI is used (parsing left to future work)
            return [{'text': res}]
    # Fallback templated questions
    questions = []
    for i in range(1, count + 1):
        questions.append({'id': i, 'text': f'{subject} sample question {i} (difficulty {difficulty})', 'answer': 'Sample answer'})
    return questions


# 2) ML result prediction (mock)
def predict_results(session: Optional[ChatSession] = None, student_id: Optional[int] = None, exam_id: Optional[int] = None) -> Dict:
    """Return a mock prediction for student performance. Replace with a real ML model later."""
    # Simple mock: random score between 40 and 95
    score = round(random.uniform(40, 95), 1)
    confidence = round(random.uniform(0.5, 0.95), 2)
    result = {'predicted_score': score, 'confidence': confidence}
    # Persist if session provided
    try:
        if session is not None:
            Prediction.objects.create(session=session, predicted_score=score, confidence=confidence)
    except Exception:
        pass
    return result


# 3) Weak area detection (mock)
def analyze_weak_areas(session: Optional[ChatSession] = None, recent_scores: Optional[List[Dict]] = None) -> List[Dict]:
    """Analyze recent performance and return weak areas as topics with severity. Mock implementation."""
    topics = ['Algebra', 'Calculus', 'Grammar', 'Comprehension', 'Physics - Kinematics']
    sampled = random.sample(topics, k=2)
    out = []
    for i, t in enumerate(sampled, start=1):
        sev = random.randint(1, 5)
        out.append({'topic': t, 'severity': sev})
        try:
            if session is not None:
                WeakArea.objects.create(session=session, topic=t, severity=sev)
        except Exception:
            pass
    return out


# 4) Smart practice test generator
def generate_practice_test(session: Optional[ChatSession], topics: List[str], num_questions: int = 10, use_openai: bool = True) -> Dict:
    """Generate a practice test focused on given topics. Returns metadata and content."""
    title = f'Practice Test: {", ".join(topics[:3])}'
    if use_openai and os.getenv('OPENAI_API_KEY'):
        prompt = f'Create a {num_questions}-question practice test covering: {", ".join(topics)}. Provide answers.'
        res = _use_openai(prompt, max_tokens=600)
        content = res if res else '\n'.join([f'Q{i}: Sample question on {topics[i % len(topics)]}' for i in range(1, num_questions + 1)])
    else:
        content = '\n'.join([f'Q{i}: Sample question on {topics[i % len(topics)]}' for i in range(1, num_questions + 1)])
    # Persist the practice test if session provided
    try:
        if session is not None:
            PracticeTest.objects.create(session=session, title=title, content=content)
    except Exception:
        pass
    return {'title': title, 'content': content}


# 5) AI Chat tutor wrapper (delegates to existing get_ai_response)
def chat_tutor_response(get_ai_response_fn, message: str, session: Optional[ChatSession]):
    """Wrapper that calls provided get_ai_response function (could be OpenAI or local)."""
    try:
        return get_ai_response_fn(message, session)
    except Exception as e:
        print('chat_tutor_response error:', e)
        return 'Sorry, I could not process that right now.'
