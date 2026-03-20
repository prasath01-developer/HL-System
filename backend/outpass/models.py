"""
Models for the Hostel Lock System (Outpass App)
"""
from django.db import models
from django.contrib.auth.models import User


class StudentStatus(models.TextChoices):
    """Canonical student presence state in hostel."""
    INSIDE = 'inside', 'Inside Hostel'
    OUTSIDE = 'outside', 'Outside Hostel'


class Student(models.Model):
    """Student model to store student information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    room_number = models.CharField(max_length=10)
    hostel_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    parent_phone = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.INSIDE,
        db_index=True,
    )
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"


class Outpass(models.Model):
    """Outpass request model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    HOSTEL_STATUS_CHOICES = [
        ('inside', 'Inside Hostel'),
        ('outside', 'Outside Hostel'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='outpasses')
    destination = models.CharField(max_length=200)
    reason = models.TextField()
    purpose = models.TextField(blank=True, null=True)  # Purpose field for API
    image = models.ImageField(upload_to='outpass_images/', blank=True, null=True)  # Image upload field
    departure_date = models.DateTimeField()
    time_out = models.DateTimeField(blank=True, null=True)  # Alias for departure_date in API
    return_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hostel_status = models.CharField(max_length=20, choices=HOSTEL_STATUS_CHOICES, default='inside')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Outpass #{self.id} - {self.student.user.get_full_name()} - {self.status}"


class Warden(models.Model):
    """Warden model for admin/warden users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=50)
    hostel_name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Warden {self.user.get_full_name()}"


# Backward-compatible alias so the domain model can also be referenced as OutpassRequest.
OutpassRequest = Outpass

