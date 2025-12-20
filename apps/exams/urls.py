"""
URL configuration for exams app.
"""
from django.urls import path, include
from . import views

app_name = 'exams'

# Admin URLs
admin_patterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('dashboard/counts/', views.admin_dashboard_counts, name='dashboard_counts'),
    
    # Subject management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Question management
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.question_create, name='question_create'),
    path('questions/<int:pk>/update/', views.question_update, name='question_update'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),
    
    # Question paper management
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/create/', views.paper_create, name='paper_create'),
    path('papers/<int:pk>/update/', views.paper_update, name='paper_update'),
    
    # Exam schedule
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
]

# Student URLs
student_patterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('<int:schedule_id>/take/', views.exam_take, name='exam_take'),
    path('<int:schedule_id>/result/', views.exam_result, name='exam_result'),
    path('history/', views.exam_history, name='exam_history'),
]

urlpatterns = [
    path('admin/', include((admin_patterns, 'admin'))),
    path('student/', include((student_patterns, 'student'))),
]
