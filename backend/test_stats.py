"""Test script to verify dashboard stats"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_project.settings')
django.setup()

from outpass.models import Student, Outpass
from django.utils import timezone

print('=== Current Data ===')
print(f'Total Students: {Student.objects.count()}')
print(f'Total Outpasses: {Outpass.objects.count()}')
print(f'Pending: {Outpass.objects.filter(status="pending").count()}')
print(f'Approved: {Outpass.objects.filter(status="approved").count()}')
print(f'Rejected: {Outpass.objects.filter(status="rejected").count()}')

# Get first student
student = Student.objects.first()
if student:
    print(f'\nFirst Student: {student.user.get_full_name()}')
    print(f'Student ID: {student.student_id}')
    print(f'Room: {student.room_number}')

# Calculate dashboard stats
now = timezone.now()
total_students = Student.objects.count()
students_outside = Outpass.objects.filter(
    status='approved',
    departure_date__lte=now,
    return_date__gte=now
).values('student').distinct().count()
students_inside = total_students - students_outside

print(f'\n=== Dashboard Calculations ===')
print(f'Total Students: {total_students}')
print(f'Inside Hostel: {students_inside}')
print(f'Outside Hostel: {students_outside}')
print(f'Pending Requests: {Outpass.objects.filter(status="pending").count()}')
print(f'Approved Requests: {Outpass.objects.filter(status="approved").count()}')
print(f'Rejected Requests: {Outpass.objects.filter(status="rejected").count()}')

# Calculate occupancy
if total_students > 0:
    occupancy = (students_inside / total_students) * 100
    print(f'Hostel Occupancy: {occupancy:.1f}%')

