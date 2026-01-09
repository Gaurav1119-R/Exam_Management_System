from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_view, name='chat_list'),
    path('chat/<int:session_id>/', views.chat_view, name='chat'),
    path('new/', views.new_chat, name='new_chat'),
    path('send/<int:session_id>/', views.send_message, name='send_message'),
    path('delete/<int:session_id>/', views.delete_session, name='delete_session'),
    path('sessions/', views.chat_list, name='chat_sessions'),
    # AI feature endpoints
    path('chat/<int:session_id>/generate_questions/', views.generate_questions_view, name='generate_questions'),
    path('chat/<int:session_id>/predict_results/', views.predict_results_view, name='predict_results'),
    path('chat/<int:session_id>/generate_practice/', views.generate_practice_view, name='generate_practice'),
]
