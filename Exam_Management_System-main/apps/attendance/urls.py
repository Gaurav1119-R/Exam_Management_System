"""
URL configuration for attendance app.
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Show schedule selector and optionally load students via exam_schedule GET param
    path('mark/', views.mark_attendance, name='mark'),
    path('mark/<int:schedule_id>/', views.mark_attendance, name='mark_with_id'),
    path('report/<int:schedule_id>/', views.attendance_report, name='report'),
    path('student-report/', views.student_attendance_report, name='student_report'),
    path('student-report/export/', views.student_attendance_export, name='student_report_export'),
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    path('register-student/', views.register_student, name='register_student'),
]