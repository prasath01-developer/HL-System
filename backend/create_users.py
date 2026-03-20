"""Script to create default users for the Hostel Lock System"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from outpass.models import Student

def create_users():
    # Create Admin/Warden User
    admin_username = 'admin'
    admin_password = 'admin123'
    
    if not User.objects.filter(username=admin_username).exists():
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email='admin@hostel.com',
            password=admin_password,
            first_name='Admin',
            last_name='Warden'
        )
        print(f"Admin user created: {admin_username} / {admin_password}")
    else:
        admin_user = User.objects.get(username=admin_username)
        print(f"Admin user already exists: {admin_username}")
    
    # Create Student User
    student_username = 'student1'
    student_password = 'student123'
    
    if not User.objects.filter(username=student_username).exists():
        student_user = User.objects.create_user(
            username=student_username,
            password=student_password,
            first_name='John',
            last_name='Doe'
        )
        
        # Create Student profile
        student = Student.objects.create(
            user=student_user,
            student_id='STU001',
            room_number='101',
            hostel_name='Block A',
            phone_number='9876543210',
            parent_phone='9876543211'
        )
        print(f"Student user created: {student_username} / {student_password}")
    else:
        print(f"Student user already exists: {student_username}")

    print("\n=== Login Credentials ===")
    print(f"Admin Panel: {admin_username} / {admin_password}")
    print(f"Student Panel: {student_username} / {student_password}")

if __name__ == '__main__':
    create_users()

