from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Welcome & Auth
    path('', views.welcome, name='welcome'),
    path('login/student/', views.login_student_view, name='login_student'),
    path('login/teacher/', views.login_teacher_view, name='login_teacher'),
    path('login/', views.login_redirect, name='login'),
    path('logout/', views.logout_view, name='logout'),
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