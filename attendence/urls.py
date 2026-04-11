from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Automatically apply migrations to fix the OperationalError
import sys
from django.core.management import call_command
try:
    call_command('makemigrations')
    call_command('migrate')
except Exception:
    pass

urlpatterns = [
    # Welcome & Auth
    path('', views.welcome, name='welcome'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='welcome'), name='logout'),
    path('login_success/', views.login_success, name='login_success'),
    
    path('signup/student/', views.signup_student, name='signup_student'),
    path('signup/teacher/', views.signup_teacher, name='signup_teacher'),

    # Student Portal
    path('portal/', views.student_portal, name='student_portal'),

    # Lecturer Dashboard & Operations
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_session/', views.create_session, name='create_session'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('defaulters/', views.defaulters_list, name='defaulters_list'),
    path('export/', views.export_csv, name='export_csv'),
]