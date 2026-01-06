"""
URL configuration for reports app.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Admin URLs
    path('admin/projects/', views.project_report_list, name='project_report_list'),
    path('admin/projects/create/', views.project_report_create, name='project_report_create'),
    path('admin/projects/<int:report_id>/grade/', views.project_report_grade, name='project_report_grade'),
    
    # Student URLs
    path('student/projects/', views.student_project_reports, name='student_project_reports'),
    path('student/projects/<int:report_id>/submit/', views.student_submit_project, name='student_submit_project'),
    path('student/performance/', views.student_performance_report, name='student_performance_report'),
]
