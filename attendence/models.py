from django.db import models



class Student(models.Model):
    usn=models.CharField(max_length=20,unique=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)

    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15,unique=True,blank=True,null=True)


    department=models.CharField(max_length=50)
    semester=models.IntegerField()

    date_of_birth=models.DateField(null=True,blank=True)
    address=models.TextField(blank=True)


    profile_image=models.ImageField(upload_to='students/',null=True,blank=True)

    is_active=models.BooleanField(default=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usn} - {self.first_name} {self.last_name}"
    

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    date = models.DateField()
    
    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent')
        ]
    )

    class Meta:
        unique_together = ['student', 'subject', 'date']   # 🔥 IMPORTANT

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} - {self.status}"

class AttendanceSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    timing = models.CharField(max_length=100, null=True, blank=True) # Deprecated
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} | {self.date} | {self.start_time} - {self.end_time}"