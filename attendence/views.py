from django.shortcuts import render, redirect
from .models import Student, Subject, Attendance, AttendanceSession
from datetime import date
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import csv

def signup_student(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_portal')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'role': 'Student'})

def signup_teacher(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'role': 'Teacher'})

def welcome(request):
    if request.user.is_authenticated:
        return redirect('login_success')
    return render(request, 'welcome.html')

@login_required
def login_success(request):
    if request.user.is_staff:
        return redirect('dashboard')
    else:
        return redirect('student_portal')

@login_required
def student_portal(request):
    sessions = AttendanceSession.objects.filter(is_active=True).order_by('-created_at')
    
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        student_name = request.POST.get('student_name', '').strip()
        usn = request.POST.get('usn', '').strip()
        
        from django.utils import timezone
        current_time = timezone.now().time()
        
        try:
            session = AttendanceSession.objects.get(id=session_id, is_active=True)
            
            if session.start_time and session.end_time:
                if not (session.start_time <= current_time <= session.end_time and session.date == date.today()):
                    messages.error(request, f"Submission rejected. {session.subject.name} is only accepting attendance from {session.start_time} to {session.end_time}.")
                    return redirect('student_portal')
            
            first_name = student_name.split()[0] if student_name else ''
            last_name = " ".join(student_name.split()[1:]) if student_name and len(student_name.split()) > 1 else ''
            
            student, created = Student.objects.get_or_create(
                usn=usn,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{usn}@student.com",
                    'department': 'Assigned Automatically',
                    'semester': 1
                }
            )
            Attendance.objects.create(
                student=student,
                subject=session.subject,
                date=session.date,
                status='Present'
            )
            messages.success(request, f"Successfully marked attendance for {session.subject.name}!")
        except AttendanceSession.DoesNotExist:
            messages.error(request, "Invalid or inactive session.")
        except IntegrityError:
            messages.warning(request, "Attention: You have already marked your attendance for this class today!")
            
        return redirect('student_portal')
        
    return render(request, 'student_portal.html', {'sessions': sessions})

@staff_member_required
def create_session(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name', '').strip()
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        
        from datetime import datetime
        start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else None
        end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None
        
        subject, created = Subject.objects.get_or_create(name=subject_name)
        
        AttendanceSession.objects.create(
            subject=subject,
            date=date.today(),
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        messages.success(request, f"Class session '{subject.name}' scheduled for today {start_time} to {end_time}!")
        return redirect('dashboard')
        
    return render(request, 'create_session.html')

@staff_member_required
def dashboard(request):
    students_count = Student.objects.count()
    subjects_count = Subject.objects.count()
    
    total_classes = Attendance.objects.count()
    present_classes = Attendance.objects.filter(status='Present').count()
    
    attendance_percentage = 0
    if total_classes > 0:
        attendance_percentage = round((present_classes / total_classes) * 100, 2)
        
    subjects = Subject.objects.all()
    chart_labels = []
    chart_data = []
    for sub in subjects:
        sub_total = Attendance.objects.filter(subject=sub).count()
        sub_present = Attendance.objects.filter(subject=sub, status='Present').count()
        chart_labels.append(sub.name)
        if sub_total > 0:
            chart_data.append(round((sub_present/sub_total)*100, 2))
        else:
            chart_data.append(0)
            
    # Purge old sessions manually if needed or just display active daily sessions
    active_sessions = AttendanceSession.objects.filter(is_active=True, date=date.today())
            
    return render(request, 'dashboard.html', {
        'students_count': students_count,
        'subjects_count': subjects_count,
        'attendance_percentage': attendance_percentage,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'active_sessions': active_sessions,
    })

@staff_member_required
def mark_attendance(request):
    students = Student.objects.all()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        selected_subject = Subject.objects.get(id=subject_id)
        selected_date = request.POST.get('date', date.today())

        for student in students:
            status = request.POST.get(f'student_{student.id}')
            if status:
                try:
                    Attendance.objects.create(
                        student=student,
                        subject=selected_subject,
                        date=selected_date,
                        status=status
                    )
                except IntegrityError:
                    pass

        return redirect('attendance_report')

    return render(request, 'mark_attendance.html', {
        'students': students,
        'subjects': subjects,
        'today': date.today().strftime('%Y-%m-%d')
    })

@staff_member_required
def attendance_report(request):
    students = Student.objects.all()
    subjects = Subject.objects.all()
    report = []
    
    subject_id = request.GET.get('subject')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    for student in students:
        qs = Attendance.objects.filter(student=student)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])
            
        total = qs.count()
        present = qs.filter(status='Present').count()

        percentage = 0
        if total > 0:
            percentage = round((present / total) * 100, 2)

        report.append({
            'student': student,
            'total': total,
            'present': present,
            'percentage': percentage
        })

    return render(request, 'attendance_report.html', {
        'report': report, 
        'subjects': subjects,
        'selected_subject': subject_id,
        'start_date': start_date,
        'end_date': end_date
    })

@staff_member_required
def defaulters_list(request):
    students = Student.objects.all()
    defaulters = []
    
    for student in students:
        total = Attendance.objects.filter(student=student).count()
        present = Attendance.objects.filter(student=student, status='Present').count()
        if total > 0:
            percentage = round((present / total) * 100, 2)
            if percentage < 75.0:
                defaulters.append({
                    'student': student,
                    'total': total,
                    'present': present,
                    'percentage': percentage
                })
                
    return render(request, 'defaulters.html', {'defaulters': defaulters})

@staff_member_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['USN', 'Name', 'Total Classes', 'Present', 'Percentage'])
    
    students = Student.objects.all()
    for student in students:
        total = Attendance.objects.filter(student=student).count()
        present = Attendance.objects.filter(student=student, status='Present').count()
        percentage = 0
        if total > 0:
            percentage = round((present / total) * 100, 2)
            
        writer.writerow([student.usn, f"{student.first_name} {student.last_name}", total, present, f"{percentage}%"])
        
    return response