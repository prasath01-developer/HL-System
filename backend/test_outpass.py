"""Test script to verify outpass details"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_project.settings')
django.setup()

from outpass.models import Student, Outpass
from django.utils import timezone

now = timezone.now()
print(f'Current Time: {now}')
print('=' * 50)

# List all outpasses
outpasses = Outpass.objects.all()
for outpass in outpasses:
    print(f'\nOutpass #{outpass.id}')
    print(f'  Student: {outpass.student.user.get_full_name()}')
    print(f'  Status: {outpass.status}')
    print(f'  Hostel Status: {outpass.hostel_status}')
    print(f'  Departure: {outpass.departure_date}')
    print(f'  Return: {outpass.return_date}')
    
    # Check if currently active
    if outpass.status == 'approved':
        if outpass.departure_date <= now <= outpass.return_date:
            print(f'  >> Currently OUTSIDE (within time range)')
        else:
            print(f'  >> Time range check: {outpass.departure_date} <= {now} <= {outpass.return_date}')

# Check students outside
print('\n' + '=' * 50)
print('Students currently outside:')
students_outside = Outpass.objects.filter(
    status='approved',
    departure_date__lte=now,
    return_date__gte=now
).values_list('student__user__first_name', 'student__user__last_name')

for s in students_outside:
    print(f'  - {s[0]} {s[1]}')

