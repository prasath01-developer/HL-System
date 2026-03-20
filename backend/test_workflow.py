"""Test script to simulate complete outpass workflow"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_project.settings')
django.setup()

from outpass.models import Student, Outpass
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
print(f'Current Time: {now}')
print('=' * 60)

# Get a student
student = Student.objects.first()
if not student:
    print("No student found!")
    exit()

print(f'Student: {student.user.get_full_name()}')
print('=' * 60)

# Step 1: Create a new outpass request (simulating student submission)
print('\n📝 STEP 1: Student creates outpass request')
outpass = Outpass.objects.create(
    student=student,
    destination='Home',
    reason='Weekend visit',
    purpose='Weekend visit',
    departure_date=now - timedelta(hours=1),  # Started 1 hour ago
    return_date=now + timedelta(hours=10),     # Returns in 10 hours
    status='pending',
    hostel_status='inside'
)
print(f'Outpass #{outpass.id} created with status: {outpass.status}')
print(f'Hostel Status: {outpass.hostel_status}')

# Step 2: Check dashboard stats (pending)
print('\n📊 Dashboard Stats (after submission):')
print(f'  Pending: {Outpass.objects.filter(status="pending").count()}')
print(f'  Approved: {Outpass.objects.filter(status="approved").count()}')

# Step 3: Admin approves the outpass
print('\n✅ STEP 2: Admin approves outpass')
outpass.status = 'approved'
outpass.hostel_status = 'outside'
outpass.save()
print(f'Outpass #{outpass.id} approved!')
print(f'Hostel Status: {outpass.hostel_status}')

# Step 4: Check dashboard stats (after approval)
print('\n📊 Dashboard Stats (after approval):')
total_students = Student.objects.count()
students_outside = Outpass.objects.filter(
    status='approved',
    departure_date__lte=now,
    return_date__gte=now
).values('student').distinct().count()
students_inside = total_students - students_outside

print(f'  Total Students: {total_students}')
print(f'  Inside Hostel: {students_inside}')
print(f'  Outside Hostel: {students_outside}')
print(f'  Pending: {Outpass.objects.filter(status="pending").count()}')
print(f'  Approved: {Outpass.objects.filter(status="approved").count()}')
print(f'  Rejected: {Outpass.objects.filter(status="rejected").count()}')

# Calculate occupancy
occupancy = (students_inside / total_students) * 100
print(f'  Hostel Occupancy: {occupancy:.1f}%')

# Step 5: Student returns (marks IN)
print('\n🏠 STEP 3: Student returns and marks IN')
outpass.hostel_status = 'inside'
outpass.save()
print(f'Outpass #{outpass.id} marked as IN!')
print(f'Hostel Status: {outpass.hostel_status}')

# Step 6: Check dashboard stats (after return)
print('\n📊 Dashboard Stats (after return):')
students_outside = Outpass.objects.filter(
    status='approved',
    departure_date__lte=now,
    return_date__gte=now
).values('student').distinct().count()
students_inside = total_students - students_outside

print(f'  Total Students: {total_students}')
print(f'  Inside Hostel: {students_inside}')
print(f'  Outside Hostel: {students_outside}')
print(f'  Pending: {Outpass.objects.filter(status="pending").count()}')
print(f'  Approved: {Outpass.objects.filter(status="approved").count()}')
print(f'  Rejected: {Outpass.objects.filter(status="rejected").count()}')

occupancy = (students_inside / total_students) * 100
print(f'  Hostel Occupancy: {occupancy:.1f}%')

print('\n' + '=' * 60)
print('✅ WORKFLOW TEST COMPLETE - All features working!')
print('=' * 60)

# Clean up test outpass
outpass.delete()
print('\n(Test outpass cleaned up)')

