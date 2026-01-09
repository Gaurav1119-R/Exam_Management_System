import os
from typing import Optional
from .models import ChatMessage


def get_ai_response(user_message: str, session) -> str:
    """
    Get response from AI based on user message.
    Currently uses a local implementation. Can be extended to use OpenAI, Hugging Face, etc.
    """
    
    # Try to use OpenAI if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        return get_openai_response(user_message, session, api_key)
    else:
        # Fallback to local implementation
        return get_local_ai_response(user_message, session)


def get_openai_response(user_message: str, session, api_key: str) -> str:
    """Get response using OpenAI API"""
    try:
        import openai
        openai.api_key = api_key
        
        # Build conversation history for context
        messages = [{"role": "system", "content": get_system_prompt()}]
        
        # Add last 5 messages for context
        context_messages = session.messages.all().order_by('created_at')[-5:]
        for msg in context_messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message['content'].strip()
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return get_local_ai_response(user_message, session)


def get_local_ai_response(user_message: str, session) -> str:
    """
    Enhanced local AI response using intelligent pattern matching and context awareness.
    This provides dynamic responses based on the actual question asked.
    """
    
    message_lower = user_message.lower().strip()
    
    # ADMIN / STAFF: provide different, admin-oriented answers
    try:
        is_staff = bool(session and getattr(session, 'user', None) and getattr(session.user, 'is_staff', False))
    except Exception:
        is_staff = False

    if is_staff:
        # Admin-level intents
        if any(word in message_lower for word in ['create', 'add', 'edit', 'publish', 'schedule', 'exam', 'test']):
            return ("Admin help — Managing exams:\n\n"
                   "• Create or edit exams from the Admin → Exams panel.\n"
                   "• Set start/end times, duration, and allowed resources.\n"
                   "• Publish the exam to make it visible to students.\n\n"
                   "Need steps to create an exam or set permissions?")
        if any(word in message_lower for word in ['student', 'users', 'enroll', 'register', 'user']):
            return ("Admin help — Managing students/users:\n\n"
                   "• Use Admin → Students to add or import student records.\n"
                   "• Edit student enrollment, departments and semesters from their profile.\n"
                   "• Use bulk-import tools for large batches.\n\n"
                   "Would you like a link to the import template?")
        if any(word in message_lower for word in ['report', 'analytics', 'export', 'performance', 'scores', 'results']):
            return ("Admin help — Reports and analytics:\n\n"
                   "• Go to Reports → Performance to view aggregate scores and trends.\n"
                   "• Use filters (department, semester, exam) to narrow results.\n"
                   "• Export CSV/PDF for administrative records.\n\n"
                   "Do you want a custom export for a specific exam or department?")
        if any(word in message_lower for word in ['attendance', 'mark', 'absent', 'presence']):
            return ("Admin help — Attendance management:\n\n"
                   "• Open Attendance → Manage to mark or adjust attendance records.\n"
                   "• Run attendance reports to see aggregate percentages and flagged students.\n\n"
                   "Need to bulk-update attendance or set thresholds?")
        # Default admin help
        return ("Admin Assistant: I can help with managing exams, students, attendance, and reports.\n"
               "Ask about creating exams, exporting reports, or managing users.")
    
    # DIRECT INTENT CHECKS: handle explicit intents even when 'exam' word is missing
    if any(word in message_lower for word in ['prepare', 'study', 'study tips', 'how to prepare', 'how do i prepare', 'how to study']):
        return ("Here are effective exam preparation tips:\n\n"
               "📚 **Study Strategy:**\n"
               "• Start studying 2-3 weeks before the exam\n"
               "• Make a study schedule and stick to it\n"
               "• Focus on topics mentioned in the syllabus\n"
               "• Take notes while studying\n\n"
               "✏️ **Practice:**\n"
               "• Solve previous year papers\n"
               "• Practice with sample questions\n"
               "• Time yourself while practicing\n"
               "• Identify weak areas and focus on them\n\n"
               "😴 **Day Before:**\n"
               "• Review important topics briefly\n"
               "• Get 7-8 hours of sleep\n"
               "• Prepare your exam hall materials\n\n"
               "💪 **Exam Day:**\n"
               "• Arrive 15 minutes early\n"
               "• Read instructions carefully\n"
               "• Attempt easy questions first\n"
               "• Manage your time wisely")

    if any(word in message_lower for word in ['result', 'results', 'score', 'scores', 'mark', 'marks', 'grade']):
        return ("Your exam results and performance can be found in the **Reports section**:\n\n"
               "1. Go to **Reports** → **Performance Report**\n"
               "2. You'll see your exam scores broken down by subject\n"
               "3. View detailed analysis including:\n"
               "   • Your score vs. total marks\n"
               "   • Percentage and grade\n"
               "   • Questions attempted\n"
               "   • Correct vs. incorrect answers\n\n"
               "Want to improve? Focus on weak areas and practice more!")
    
    # EXAM-RELATED QUESTIONS - CHECK FIRST (more specific)
    if any(word in message_lower for word in ['exam', 'test', 'quiz', 'assessment']):
        # Specific timing questions
        if 'when' in message_lower or 'date' in message_lower or 'time' in message_lower:
            if 'next' in message_lower:
                return "Your next exam details are displayed in the dashboard. Click on the exam name to see the exact date, time, and duration. You can also check the full exam schedule in the Exams section."
            elif 'all' in message_lower or 'list' in message_lower or 'schedule' in message_lower:
                return "You can view all upcoming exams in the dashboard. Each exam shows the date, time, and duration. Click on any exam to get more details about the topics covered and exam instructions."
            else:
                return "To check exam schedules, go to your dashboard or the Exams section. You'll see all upcoming exams with their dates, times, and venues listed."
        
        # Preparation questions
        elif any(word in message_lower for word in ['prepare', 'study', 'tips', 'way', 'start']):
            return ("Here are effective exam preparation tips:\n\n"
                   "📚 **Study Strategy:**\n"
                   "• Start studying 2-3 weeks before the exam\n"
                   "• Make a study schedule and stick to it\n"
                   "• Focus on topics mentioned in the syllabus\n"
                   "• Take notes while studying\n\n"
                   "✏️ **Practice:**\n"
                   "• Solve previous year papers\n"
                   "• Practice with sample questions\n"
                   "• Time yourself while practicing\n"
                   "• Identify weak areas and focus on them\n\n"
                   "😴 **Day Before:**\n"
                   "• Review important topics briefly\n"
                   "• Get 7-8 hours of sleep\n"
                   "• Prepare your exam hall materials\n\n"
                   "💪 **Exam Day:**\n"
                   "• Arrive 15 minutes early\n"
                   "• Read instructions carefully\n"
                   "• Attempt easy questions first\n"
                   "• Manage your time wisely")
        
        # Results/Score questions
        elif any(word in message_lower for word in ['result', 'score', 'mark', 'performance', 'grade']):
            return ("Your exam results and performance can be found in the **Reports section**:\n\n"
                   "1. Go to **Reports** → **Performance Report**\n"
                   "2. You'll see your exam scores broken down by subject\n"
                   "3. View detailed analysis including:\n"
                   "   • Your score vs. total marks\n"
                   "   • Percentage and grade\n"
                   "   • Questions attempted\n"
                   "   • Correct vs. incorrect answers\n\n"
                   "Want to improve? Focus on weak areas and practice more!")
        
        # Duration/difficulty
        elif any(word in message_lower for word in ['duration', 'long', 'how many', 'difficult', 'hard', 'easy']):
            return ("Exam details including duration and difficulty level are shown in:\n"
                   "• The exam card in your dashboard\n"
                   "• The detailed exam information page\n\n"
                   "Typically, exams have different durations based on the number of questions. "
                   "The system will show you the exact time limit when you start the exam.")
        
        # Rules/instructions
        elif any(word in message_lower for word in ['rule', 'instruction', 'guideline', 'allowed', 'can i']):
            return ("Important exam rules and instructions:\n\n"
                   "✓ **Allowed:**\n"
                   "• Use the provided exam interface\n"
                   "• Take notes (if permitted)\n"
                   "• Use calculator for math exams (if allowed)\n\n"
                   "✗ **NOT Allowed:**\n"
                   "• Switching to other windows/tabs\n"
                   "• Using unauthorized materials\n"
                   "• Discussing questions with others\n"
                   "• Taking screenshots\n\n"
                   "The system automatically detects violations. Follow all guidelines strictly!")
        
        else:
            return ("I can help with exam-related questions! Ask me about:\n"
                   "• **When** is my next exam?\n"
                   "• **How** do I prepare for exams?\n"
                   "• What are my **exam results**?\n"
                   "• What are the **exam rules**?\n"
                   "• How **long** is the exam?\n\n"
                   "What would you like to know?")
    
    # ATTENDANCE-RELATED QUESTIONS - CHECK SECOND
    elif any(word in message_lower for word in ['attendance', 'absent', 'present', 'skipped', 'class', 'percentage']):
        if 'how' in message_lower or 'check' in message_lower or 'view' in message_lower:
            return ("To check your attendance:\n\n"
                   "1. Click on **Attendance Report** in the sidebar\n"
                   "2. You'll see:\n"
                   "   • Total classes held\n"
                   "   • Classes attended\n"
                   "   • Classes skipped\n"
                   "   • Attendance percentage\n"
                   "   • Detailed attendance records\n\n"
                   "Maintain at least 75% attendance to be eligible for exams!")
        elif 'percentage' in message_lower or 'mark' in message_lower:
            return ("Your attendance percentage is calculated as:\n\n"
                   "**Attendance % = (Classes Attended / Total Classes) × 100**\n\n"
                   "Most institutions require at least 75% attendance. Check your Attendance Report for detailed breakdown.")
        else:
            return ("Need help with attendance?\n"
                   "• View your attendance report\n"
                   "• Check attendance percentage\n"
                   "• Understand attendance requirements\n\n"
                   "Go to **Attendance Report** to see all details!")
    
    # PERFORMANCE/PROGRESS QUESTIONS - CHECK THIRD
    elif any(word in message_lower for word in ['performance', 'progress', 'improvement', 'weak', 'strong', 'best', 'worst']):
        return ("To analyze your academic performance:\n\n"
               "1. Go to **Reports** → **Performance Report**\n"
               "2. Review your exam scores by subject\n"
               "3. Identify strong and weak areas\n\n"
               "**Tips to improve:**\n"
               "• Focus more on weak subjects\n"
               "• Solve more practice problems\n"
               "• Join study groups\n"
               "• Ask instructors for help\n"
               "• Review mistakes regularly\n\n"
               "Consistent effort leads to better results! 💪")
    
    # GREETING/FRIENDLY QUESTIONS - CHECK BEFORE GENERAL
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'thanks', 'thank you', 'good morning', 'good afternoon']):
        if 'thanks' in message_lower or 'thank' in message_lower:
            return "You're welcome! 😊 Feel free to ask me anything about exams, attendance, or how to use the system. I'm always here to help!"
        else:
            return ("Hello! 👋 Welcome to the Exam Management System!\n\n"
                   "I'm your AI Assistant. I can help you with:\n"
                   "• 📅 Exam schedules and dates\n"
                   "• 📚 Study tips and preparation\n"
                   "• 📊 Your exam results and performance\n"
                   "• ✅ Attendance tracking\n"
                   "• 🗺️ System navigation\n\n"
                   "What can I assist you with today?")
    
    # MOTIVATIONAL/ENCOURAGEMENT - CHECK BEFORE GENERAL
    elif any(word in message_lower for word in ['stressed', 'anxious', 'worried', 'nervous', 'scared', 'tough']):
        return ("Don't worry! You've got this! 💪\n\n"
               "**Remember:**\n"
               "• You've prepared for this\n"
               "• Stress is normal and manageable\n"
               "• Deep breathing helps calm nerves\n"
               "• Focus on what you know\n"
               "• One question at a time\n\n"
               "**Before exam:**\n"
               "• Get good sleep\n"
               "• Eat a healthy breakfast\n"
               "• Arrive early to relax\n"
               "• Believe in yourself!\n\n"
               "You'll do great! 🌟")
    
    # SPECIFIC SUBJECT QUESTIONS
    elif 'math' in message_lower or 'english' in message_lower or 'science' in message_lower or 'physics' in message_lower or 'chemistry' in message_lower:
        subject = 'Math' if 'math' in message_lower else ('English' if 'english' in message_lower else ('Science' if 'science' in message_lower else ('Physics' if 'physics' in message_lower else 'Chemistry')))
        if 'exam' in message_lower:
            return f"For your {subject} exam:\n\n✓ Check the exam schedule in your dashboard\n✓ Review the syllabus and topics\n✓ Practice with sample questions\n✓ Clarify doubts with your instructor\n\nGood luck! You can do this! 💪"
        else:
            return f"Interested in {subject}? I can help with:\n• Exam information\n• Study tips\n• Performance analysis\n\nWhat would you like to know about {subject}?"
    
    # GENERAL NAVIGATION/HELP - CHECK LAST (least specific)
    elif any(word in message_lower for word in ['how', 'where', 'what', 'navigate', 'use', 'access', 'feature', 'section']):
        if 'subject' in message_lower:
            return ("To manage your subjects:\n\n"
                   "1. Go to **Exams** → **Subjects**\n"
                   "2. You'll see all available subjects\n"
                   "3. View subject details and related exams\n"
                   "4. Check study materials if available")
        elif 'dashboard' in message_lower:
            return ("Your **Dashboard** is the main hub showing:\n"
                   "• Statistics (Total exams, Completed, Upcoming)\n"
                   "• Upcoming exams list\n"
                   "• Past exams and results\n"
                   "• Quick action links\n\n"
                   "This is where you start your exam journey!")
        elif 'profile' in message_lower or 'account' in message_lower:
            return ("To access your profile:\n\n"
                   "1. Click your name in the top right\n"
                   "2. Select **My Profile**\n"
                   "3. View/edit:\n"
                   "   • Personal information\n"
                   "   • Contact details\n"
                   "   • Department and semester\n"
                   "   • Profile picture")
        else:
            return ("I can help you navigate! Ask me about:\n"
                   "• How do I access **[feature]**?\n"
                   "• Where is the **[section]**?\n"
                   "• How do I use **[tool]**?\n"
                   "• What does **[feature]** do?\n\n"
                   "What would you like help with?")
    
    # DEFAULT - UNKNOWN QUESTION
    else:
        return ("I didn't fully understand that question, but I'm here to help! 😊\n\n"
               "Try asking me about:\n"
               "• **Exams:** When, how to prepare, results\n"
               "• **Attendance:** Check percentage, view records\n"
               "• **Performance:** Analyze scores, improvement tips\n"
               "• **Navigation:** How to use different features\n\n"
               f"Or rephrase your question and I'll do my best to help!")



def get_system_prompt() -> str:
    """Get the system prompt for the AI assistant"""
    return """You are a helpful AI Assistant for an Exam Management System. You help students with:
1. Exam schedules, dates, and venue information
2. Study and exam preparation tips
3. Understanding their academic performance
4. Tracking attendance
5. General navigation and how to use the system

Be friendly, helpful, and professional. Provide clear and concise answers. 
When a student needs to check specific data (like their exam schedule or results), 
direct them to the appropriate section of the application."""
