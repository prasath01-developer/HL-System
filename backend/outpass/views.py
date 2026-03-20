"""
Views for the Hostel Lock System (Outpass App)
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Outpass, Student, StudentStatus
from .forms import OutpassForm
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, OuterRef, Subquery


def _set_student_status(student, hostel_status):
    """Synchronize student presence with outpass hostel status."""
    student.status = StudentStatus.OUTSIDE if hostel_status == 'outside' else StudentStatus.INSIDE
    student.save(update_fields=['status'])


def _get_dashboard_counts():
    """Single source for admin dashboard counters."""
    total_students = Student.objects.count()
    students_inside = Student.objects.filter(status=StudentStatus.INSIDE).count()
    students_outside = Student.objects.filter(status=StudentStatus.OUTSIDE).count()
    pending_requests = Outpass.objects.filter(status='pending').count()
    approved_requests = Outpass.objects.filter(status='approved').count()
    rejected_requests = Outpass.objects.filter(status='rejected').count()
    total_requests = Outpass.objects.count()
    occupancy_percentage = round((students_inside / total_students) * 100, 1) if total_students else 0

    return {
        'total_students': total_students,
        'students_inside': students_inside,
        'students_outside': students_outside,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'total_requests': total_requests,
        'occupancy_percentage': occupancy_percentage,
    }


# =============================================================================
# REST API Login View
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def login_api_view(request):
    """
    REST API endpoint for user login.
    
    Accepts JSON: {"username": "...", "password": "..."}
    Returns JSON: {"success": true/false, "message": "...", "redirect": "..."}
    """
    try:
        # Parse JSON request body
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required.'
            }, status=400)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            login(request, user)
            
            # Determine redirect based on user role
            if user.is_staff:
                redirect_url = '/admin-dashboard/'
            else:
                redirect_url = '/dashboard/'
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful!',
                'redirect': redirect_url,
                'user': {
                    'username': user.username,
                    'is_admin': user.is_staff,
                    'is_student': not user.is_staff
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password.'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Complete Admin Dashboard Statistics (Enhanced)
# =============================================================================

@login_required
def admin_dashboard_complete_stats_api(request):
    """
    REST API endpoint to get complete admin dashboard statistics.
    
    Returns JSON:
    {
        "success": true,
        "data": {
            "total_students": <int>,
            "students_inside": <int>,
            "students_outside": <int>,
            "pending_requests": <int>,
            "approved_requests": <int>,
            "rejected_requests": <int>,
            "total_requests": <int>
        }
    }
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        stats = _get_dashboard_counts()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_students': stats['total_students'],
                'students_inside': stats['students_inside'],
                'students_outside': stats['students_outside'],
                'pending_requests': stats['pending_requests'],
                'approved_requests': stats['approved_requests'],
                'rejected_requests': stats['rejected_requests'],
                'total_requests': stats['total_requests'],
                'occupancy_percentage': stats['occupancy_percentage'],
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Mark Student IN/OUT
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_student_status(request):
    """
    API to mark student as Inside or Outside.
    
    Accepts JSON: {"outpass_id": <int>, "hostel_status": "inside"|"outside"}
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        outpass_id = data.get('outpass_id')
        hostel_status = data.get('hostel_status')
        
        if not outpass_id:
            return JsonResponse({
                'success': False,
                'message': 'Outpass ID is required.'
            }, status=400)
        
        if hostel_status not in ['inside', 'outside']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status. Use "inside" or "outside".'
            }, status=400)
        
        outpass = get_object_or_404(Outpass, id=outpass_id)
        outpass.hostel_status = hostel_status
        outpass.save(update_fields=['hostel_status', 'updated_at'])
        _set_student_status(outpass.student, hostel_status)
        
        return JsonResponse({
            'success': True,
            'message': f'Student marked as {hostel_status} successfully!',
            'data': {
                'outpass_id': outpass.id,
                'hostel_status': outpass.hostel_status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Approve/Reject Outpass (AJAX)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_outpass_status(request):
    """
    API to approve or reject an outpass request.
    
    Accepts JSON: {"outpass_id": <int>, "action": "approve"|"reject"}
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        outpass_id = data.get('outpass_id')
        action = data.get('action')
        
        if not outpass_id:
            return JsonResponse({
                'success': False,
                'message': 'Outpass ID is required.'
            }, status=400)
        
        if action not in ['approve', 'reject']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action. Use "approve" or "reject".'
            }, status=400)
        
        outpass = get_object_or_404(Outpass, id=outpass_id)
        
        if action == 'approve':
            outpass.status = 'approved'
            outpass.hostel_status = 'outside'
            outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
            _set_student_status(outpass.student, 'outside')
            message = f'Outpass #{outpass_id} approved successfully!'
        else:
            outpass.status = 'rejected'
            outpass.hostel_status = 'inside'
            outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
            _set_student_status(outpass.student, 'inside')
            message = f'Outpass #{outpass_id} rejected.'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'data': {
                'outpass_id': outpass.id,
                'status': outpass.status,
                'hostel_status': outpass.hostel_status
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Student Management (Admin)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_student_api(request):
    """
    API to create a new student account.
    
    Accepts JSON:
    {
        "first_name": "...",
        "last_name": "...",
        "username": "...",
        "password": "...",
        "confirm_password": "...",
        "student_id": "...",
        "room_number": "...",
        "hostel_name": "...",
        "phone_number": "...",
        "parent_phone": "...",
        "department": "...",
        "status": "inside" | "outside"
    }
    
    Returns JSON: {"success": true/false, "message": "...", "student_id": ...}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Extract fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        student_id = data.get('student_id', '').strip()
        room_number = data.get('room_number', '').strip()
        hostel_name = data.get('hostel_name', 'Main Hostel')
        phone_number = data.get('phone_number', '').strip()
        parent_phone = data.get('parent_phone', '').strip()
        department = data.get('department', '').strip()
        status = data.get('status', StudentStatus.INSIDE)
        
        # Validation
        errors = {}
        
        if not first_name:
            errors['first_name'] = 'First name is required.'
        if not last_name:
            errors['last_name'] = 'Last name is required.'
        if not username:
            errors['username'] = 'Username is required.'
        if not student_id:
            errors['student_id'] = 'Register number is required.'
        if not room_number:
            errors['room_number'] = 'Room number is required.'
        if not phone_number:
            errors['phone_number'] = 'Phone number is required.'
        if not password:
            errors['password'] = 'Password is required.'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'
        if status not in [StudentStatus.INSIDE, StudentStatus.OUTSIDE]:
            errors['status'] = 'Status must be "inside" or "outside".'
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        
        # Check if student_id already exists
        if Student.objects.filter(student_id=student_id).exists():
            errors['student_id'] = 'Register number already exists.'
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed.',
                'errors': errors
            }, status=400)
        
        # Create User
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=data.get('email', f'{username}@hostel.edu')
        )
        
        # Create Student profile
        student = Student.objects.create(
            user=user,
            student_id=student_id,
            room_number=room_number,
            hostel_name=hostel_name,
            phone_number=phone_number,
            parent_phone=parent_phone,
            status=status,
        )
        
        # Store additional fields in user profile if needed
        # (Department can be added to Student model if required)
        
        return JsonResponse({
            'success': True,
            'message': f'Student account created successfully!',
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'username': username,
                'full_name': f'{first_name} {last_name}',
                'room_number': room_number,
                'phone_number': phone_number
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
def get_all_students_api(request):
    """
    API to get all students.
    
    Query Parameters:
    - search: search by name, student_id, or username
    - status: filter by hostel status (inside, outside)
    
    Returns JSON with list of students.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        # Base queryset
        students = Student.objects.select_related('user').order_by('-id')
        
        # Apply filters
        if search_query:
            students = students.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(student_id__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
        
        if status_filter in [StudentStatus.INSIDE, StudentStatus.OUTSIDE]:
            students = students.filter(status=status_filter)

        # Serialize data
        student_list = []
        for student in students:
            student_list.append({
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.user.get_full_name(),
                'username': student.user.username,
                'email': student.user.email,
                'room_number': student.room_number,
                'hostel_name': student.hostel_name,
                'phone_number': student.phone_number,
                'parent_phone': student.parent_phone,
                'current_status': student.status,
                'is_active': student.user.is_active,
                'date_joined': student.user.date_joined.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'count': len(student_list),
            'data': student_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
def get_student_api(request, student_id):
    """
    API to get a single student by ID.
    
    Returns JSON with student details.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        student = get_object_or_404(Student, id=student_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.user.get_full_name(),
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'username': student.user.username,
                'email': student.user.email,
                'room_number': student.room_number,
                'hostel_name': student.hostel_name,
                'phone_number': student.phone_number,
                'parent_phone': student.parent_phone,
                'status': student.status,
                'is_active': student.user.is_active,
                'date_joined': student.user.date_joined.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_student_api(request, student_id):
    """
    API to update student information.
    
    Accepts JSON with fields to update.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=student_id)
        user = student.user
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'email' in data:
            user.email = data['email'].strip()
        
        user.save()
        
        # Update student fields
        if 'room_number' in data:
            student.room_number = data['room_number'].strip()
        if 'hostel_name' in data:
            student.hostel_name = data['hostel_name'].strip()
        if 'phone_number' in data:
            student.phone_number = data['phone_number'].strip()
        if 'parent_phone' in data:
            student.parent_phone = data['parent_phone'].strip()
        if 'student_id' in data:
            # Check if new student_id is unique
            if Student.objects.exclude(id=student_id).filter(student_id=data['student_id']).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Register number already exists.'
                }, status=400)
            student.student_id = data['student_id'].strip()
        if 'status' in data and data['status'] in [StudentStatus.INSIDE, StudentStatus.OUTSIDE]:
            student.status = data['status']
        
        student.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Student updated successfully!',
            'data': {
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.user.get_full_name(),
                'room_number': student.room_number,
                'phone_number': student.phone_number,
                'status': student.status,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_student_api(request, student_id):
    """
    API to delete a student account.
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        student = get_object_or_404(Student, id=student_id)
        user = student.user
        student_name = student.user.get_full_name()
        
        # Delete student profile (will cascade to outpasses if on_delete=CASCADE)
        student.delete()
        
        # Delete user account
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Student "{student_name}" deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reset_student_password_api(request, student_id):
    """
    API to reset a student's password.
    
    Accepts JSON: {"new_password": "..."}
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        new_password = data.get('new_password', '').strip()
        
        if not new_password:
            return JsonResponse({
                'success': False,
                'message': 'New password is required.'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters.'
            }, status=400)
        
        student = get_object_or_404(Student, id=student_id)
        user = student.user
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Password for "{student.user.get_full_name()}" has been reset successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
def get_student_movement_api(request):
    """
    API to get student movement history for line chart.
    
    Returns JSON with daily movement data for the last 7 days.
    Snapshot rule per day:
    - If student's latest decision up to that day is approved => outside
    - Otherwise => inside
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        now = timezone.now()
        days = int(request.GET.get('days', 7))
        days = max(1, min(days, 31))
        
        labels = []
        inside_counts = []
        outside_counts = []
        
        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            latest_decision_subquery = (
                Outpass.objects
                .filter(
                    student=OuterRef('pk'),
                    status__in=['approved', 'rejected'],
                    updated_at__lte=day_end,
                )
                .order_by('-updated_at')
                .values('status')[:1]
            )

            students_with_snapshot = Student.objects.annotate(
                latest_decision=Subquery(latest_decision_subquery)
            )

            outside_count = students_with_snapshot.filter(latest_decision='approved').count()
            inside_count = students_with_snapshot.exclude(latest_decision='approved').count()
            
            labels.append(day.strftime('%d %b'))
            inside_counts.append(inside_count)
            outside_counts.append(outside_count)
        
        return JsonResponse({
            'success': True,
            'data': {
                'labels': labels,
                'inside': inside_counts,
                'outside': outside_counts
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
def get_occupancy_percentage_api(request):
    """
    API to get hostel occupancy percentage.
    
    Returns JSON with occupancy data.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        stats = _get_dashboard_counts()
        total_students = stats['total_students']
        students_inside = stats['students_inside']
        students_outside = stats['students_outside']

        return JsonResponse({
            'success': True,
            'data': {
                'total_students': total_students,
                'students_inside': students_inside,
                'students_outside': students_outside,
                'occupancy_percentage': stats['occupancy_percentage'],
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Get All Outpasses with Filters
# =============================================================================

@login_required
def get_outpasses_api(request):
    """
    API to get all outpasses with optional filters.
    
    Query Parameters:
    - status: filter by status (pending, approved, rejected)
    - date: filter by date (YYYY-MM-DD)
    - search: search by student name or ID
    - hostel_status: filter by hostel status (inside, outside)
    
    Returns JSON with list of outpasses.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        # Get query parameters
        status_filter = request.GET.get('status', '')
        date_filter = request.GET.get('date', '')
        search_query = request.GET.get('search', '')
        hostel_status_filter = request.GET.get('hostel_status', '')
        
        # Base queryset
        outpasses = Outpass.objects.select_related('student__user').order_by('-created_at')
        
        # Apply filters
        if status_filter:
            outpasses = outpasses.filter(status=status_filter)
        
        if date_filter:
            outpasses = outpasses.filter(created_at__date=date_filter)
        
        if hostel_status_filter:
            outpasses = outpasses.filter(hostel_status=hostel_status_filter)
        
        if search_query:
            outpasses = outpasses.filter(
                Q(student__user__first_name__icontains=search_query) |
                Q(student__user__last_name__icontains=search_query) |
                Q(student__student_id__icontains=search_query)
            )
        
        # Serialize data
        outpass_list = []
        for outpass in outpasses:
            outpass_list.append({
                'id': outpass.id,
                'student_name': outpass.student.user.get_full_name(),
                'student_id': outpass.student.student_id,
                'destination': outpass.destination,
                'purpose': outpass.purpose or outpass.reason,
                'departure_time': outpass.departure_date.strftime('%Y-%m-%d %H:%M'),
                'return_time': outpass.return_date.strftime('%Y-%m-%d %H:%M'),
                'status': outpass.status,
                'hostel_status': outpass.hostel_status,
                'created_at': outpass.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'count': len(outpass_list),
            'data': outpass_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Daily Outpass Requests Chart Data
# =============================================================================

@login_required
def get_daily_requests_chart(request):
    """
    API to get daily outpass requests for the last 7 days.
    
    Returns JSON with daily counts.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        now = timezone.now()
        days = []
        labels = []
        
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = Outpass.objects.filter(
                created_at__gte=day_start,
                created_at__lte=day_end
            ).count()
            
            labels.append(day.strftime('%a'))
            days.append(count)
        
        return JsonResponse({
            'success': True,
            'data': {
                'labels': labels,
                'counts': days
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Students Inside vs Outside Chart Data
# =============================================================================

@login_required
def get_hostel_status_chart(request):
    """
    API to get students inside vs outside data.
    
    Returns JSON with counts.
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        stats = _get_dashboard_counts()

        return JsonResponse({
            'success': True,
            'data': {
                'labels': ['Inside Hostel', 'Outside Hostel'],
                'counts': [stats['students_inside'], stats['students_outside']]
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# CSRF Token View (for frontend to get token)
# =============================================================================

def get_csrf_token(request):
    """
    API endpoint to get CSRF token for frontend.
    """
    return JsonResponse({'csrf_token': request.META.get('CSRF_COOKIE', '')})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

def home(request):
    return render(request, 'login.html')

@login_required
def dashboard(request):
    """Student dashboard view"""
    if request.user.is_staff:
        return render(request, 'dashboard.html', {
            'student': None,
            'outpasses': [],
            'error': 'Student view is only available for student accounts.'
        })

    try:
        student = Student.objects.get(user=request.user)
        outpasses = Outpass.objects.filter(student=student).order_by('-created_at')
        return render(request, 'dashboard.html', {
            'student': student,
            'outpasses': outpasses
        })
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return render(request, 'dashboard.html', {
            'student': None,
            'outpasses': [],
            'error': 'Student profile not found'
        })


@login_required
def create_pass(request):
    """Create new outpass request"""
    if request.method == 'POST':
        form = OutpassForm(request.POST)
        if form.is_valid():
            outpass = form.save(commit=False)
            student = Student.objects.get(user=request.user)
            outpass.student = student
            outpass.status = 'pending'
            outpass.hostel_status = 'inside'
            outpass.save()
            messages.success(request, "Outpass request submitted successfully!")
            return redirect('dashboard')
    else:
        form = OutpassForm()
    return render(request, 'create_pass.html', {'form': form})


@login_required
def create_pass_api_view(request):
    """Render the API-based outpass creation form"""
    return render(request, 'create_outpass_api.html')


@login_required
def admin_dashboard(request):
    """Admin/Warden dashboard view"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    stats = _get_dashboard_counts()
    pending_outpasses = Outpass.objects.filter(status='pending').order_by('-created_at')
    outside_outpasses = Outpass.objects.filter(status='approved').order_by('-updated_at')
    inside_outpasses = Outpass.objects.filter(status='rejected').order_by('-updated_at')
    all_outpasses = Outpass.objects.all().order_by('-created_at')
    
    return render(request, 'admin_dashboard.html', {
        'stats': stats,
        'pending_outpasses': pending_outpasses,
        'outside_outpasses': outside_outpasses,
        'inside_outpasses': inside_outpasses,
        'all_outpasses': all_outpasses
    })


@login_required
def approve_outpass(request, outpass_id):
    """Approve outpass request"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    outpass = Outpass.objects.get(id=outpass_id)
    outpass.status = 'approved'
    outpass.hostel_status = 'outside'
    outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
    _set_student_status(outpass.student, 'outside')
    messages.success(request, f"Outpass #{outpass_id} approved!")
    return redirect('admin_dashboard')


@login_required
def reject_outpass(request, outpass_id):
    """Reject outpass request"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    outpass = Outpass.objects.get(id=outpass_id)
    outpass.status = 'rejected'
    outpass.hostel_status = 'inside'
    outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
    _set_student_status(outpass.student, 'inside')
    messages.warning(request, f"Outpass #{outpass_id} rejected!")
    return redirect('admin_dashboard')


@login_required
def delete_outpass(request, outpass_id):
    """
    Delete an outpass request permanently.
    
    This view handles the deletion of outpass requests from the admin dashboard.
    Only admin/warden users can delete outpass requests.
    """
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    try:
        outpass = Outpass.objects.get(id=outpass_id)
        outpass_id_display = outpass.id
        outpass.delete()
        messages.success(request, f"Outpass #{outpass_id_display} deleted successfully!")
    except Outpass.DoesNotExist:
        messages.error(request, f"Outpass #{outpass_id} not found.")
    except Exception as e:
        messages.error(request, f"Error deleting outpass: {str(e)}")
    
    return redirect('admin_dashboard')


# =============================================================================
# REST API: Logout
# =============================================================================

@login_required
@require_http_methods(["POST"])
def logout_api_view(request):
    """
    REST API endpoint for user logout.
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    try:
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful!',
            'redirect': '/login/'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Get My Outpasses (Student's Own Outpasses)
# =============================================================================

@login_required
def my_outpasses_api(request):
    """
    REST API endpoint for students to get their own outpass requests.
    
    Query Parameters:
    - status: filter by status (pending, approved, rejected)
    
    Returns JSON with list of student's outpasses.
    """
    try:
        # Get student profile
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Student profile not found.'
            }, status=404)
        
        # Get optional status filter
        status_filter = request.GET.get('status', '')
        
        # Base queryset - only this student's outpasses
        outpasses = Outpass.objects.filter(student=student).order_by('-created_at')
        
        # Apply status filter if provided
        if status_filter:
            outpasses = outpasses.filter(status=status_filter)
        
        # Serialize data
        outpass_list = []
        for outpass in outpasses:
            outpass_data = {
                'id': outpass.id,
                'destination': outpass.destination,
                'purpose': outpass.purpose or outpass.reason,
                'departure_date': outpass.departure_date.strftime('%Y-%m-%d %H:%M'),
                'return_date': outpass.return_date.strftime('%Y-%m-%d %H:%M'),
                'status': outpass.status,
                'status_display': outpass.get_status_display(),
                'hostel_status': outpass.hostel_status,
                'hostel_status_display': outpass.get_hostel_status_display(),
                'created_at': outpass.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Add image URL if available
            if outpass.image:
                outpass_data['image_url'] = outpass.image.url
            else:
                outpass_data['image_url'] = None
                
            outpass_list.append(outpass_data)
        
        return JsonResponse({
            'success': True,
            'count': len(outpass_list),
            'data': outpass_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Mark Student IN (Student marks themselves as inside)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_in_api(request):
    """
    API for students to mark themselves as "IN" (inside hostel).
    
    This is typically used when a student returns from an outpass.
    
    Accepts JSON: {"outpass_id": <int>}
    OR: {} (marks the most recent approved outpass as "in")
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    try:
        # Get student profile
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Student profile not found.'
            }, status=404)
        
        # Parse request body (optional)
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}
        
        outpass_id = data.get('outpass_id')
        
        if outpass_id:
            # Mark specific outpass as "in"
            try:
                outpass = Outpass.objects.get(id=outpass_id, student=student)
                outpass.hostel_status = 'inside'
                outpass.save(update_fields=['hostel_status', 'updated_at'])
                _set_student_status(student, 'inside')
                return JsonResponse({
                    'success': True,
                    'message': f'Outpass #{outpass_id} marked as IN successfully!',
                    'data': {
                        'outpass_id': outpass.id,
                        'hostel_status': outpass.hostel_status
                    }
                })
            except Outpass.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Outpass not found or does not belong to you.'
                }, status=404)
        else:
            # Find the most recent approved outpass that's currently "outside"
            latest_outside = Outpass.objects.filter(
                student=student,
                status='approved',
                hostel_status='outside'
            ).order_by('-departure_date').first()
            
            if latest_outside:
                latest_outside.hostel_status = 'inside'
                latest_outside.save(update_fields=['hostel_status', 'updated_at'])
                _set_student_status(student, 'inside')
                return JsonResponse({
                    'success': True,
                    'message': f'Outpass #{latest_outside.id} marked as IN successfully!',
                    'data': {
                        'outpass_id': latest_outside.id,
                        'hostel_status': latest_outside.hostel_status
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No active outpass found to mark as IN.'
                }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Approve Outpass (RESTful endpoint)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def approve_outpass_api(request, outpass_id):
    """
    REST API endpoint to approve an outpass request.
    
    URL: POST /api/admin/approve/<id>/
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        outpass = get_object_or_404(Outpass, id=outpass_id)
        outpass.status = 'approved'
        outpass.hostel_status = 'outside'
        outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
        _set_student_status(outpass.student, 'outside')
        
        return JsonResponse({
            'success': True,
            'message': f'Outpass #{outpass_id} approved successfully!',
            'data': {
                'outpass_id': outpass.id,
                'status': outpass.status,
                'hostel_status': outpass.hostel_status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Reject Outpass (RESTful endpoint)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reject_outpass_api(request, outpass_id):
    """
    REST API endpoint to reject an outpass request.
    
    URL: POST /api/admin/reject/<id>/
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        outpass = get_object_or_404(Outpass, id=outpass_id)
        outpass.status = 'rejected'
        outpass.hostel_status = 'inside'
        outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
        _set_student_status(outpass.student, 'inside')
        
        return JsonResponse({
            'success': True,
            'message': f'Outpass #{outpass_id} rejected.',
            'data': {
                'outpass_id': outpass.id,
                'status': outpass.status,
                'hostel_status': outpass.hostel_status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Delete Outpass (AJAX)
# =============================================================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_outpass_api(request, outpass_id):
    """
    REST API endpoint to delete an outpass request.
    
    URL: POST /api/admin/delete-outpass/<id>/
    
    Returns JSON: {"success": true/false, "message": "..."}
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        outpass = get_object_or_404(Outpass, id=outpass_id)
        outpass.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Outpass #{outpass_id} deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Admin Dashboard Statistics
# =============================================================================

@login_required
def admin_dashboard_stats_api(request):
    """
    REST API endpoint to get admin dashboard statistics.
    
    Returns JSON:
    {
        "success": true,
        "data": {
            "total_students": <int>,
            "total_out_students": <int>,
            "total_inside_students": <int>,
            "total_pending_requests": <int>
        }
    }
    
    Requirements:
    - User must be logged in (login_required)
    - User must be staff/admin (is_staff)
    """
    # Check if user has admin privileges
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        }, status=403)
    
    try:
        stats = _get_dashboard_counts()

        return JsonResponse({
            'success': True,
            'data': {
                'total_students': stats['total_students'],
                'students_inside': stats['students_inside'],
                'students_outside': stats['students_outside'],
                'pending_requests': stats['pending_requests'],
                'approved_requests': stats['approved_requests'],
                'rejected_requests': stats['rejected_requests'],
                # Backward compatible keys for existing clients:
                'total_out_students': stats['students_outside'],
                'total_inside_students': stats['students_inside'],
                'total_pending_requests': stats['pending_requests'],
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# =============================================================================
# REST API: Create Outpass (using Fetch API + FormData)
# =============================================================================

@login_required
def create_outpass_api(request):
    """
    REST API endpoint to create an outpass request.
    
    Accepts FormData with:
    - purpose: Text description of the purpose
    - image: Image file (optional)
    - time_out: Datetime string (YYYY-MM-DDTHH:MM)
    - destination: Destination address
    - return_date: Return datetime string (YYYY-MM-DDTHH:MM)
    
    Returns JSON response:
    - Success: {"success": true, "message": "...", "outpass_id": ...}
    - Error: {"success": false, "errors": {...}}
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST method is allowed.'
        }, status=405)
    
    try:
        # Get student profile
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Student profile not found. Please contact admin.'
            }, status=400)
        
        # Extract data from FormData
        purpose = request.POST.get('purpose', '').strip()
        destination = request.POST.get('destination', '').strip()
        time_out_str = request.POST.get('time_out', '').strip()
        return_date_str = request.POST.get('return_date', '').strip()
        image = request.FILES.get('image')
        
        # Validation errors
        errors = {}
        
        if not purpose:
            errors['purpose'] = 'Purpose is required.'
        
        if not destination:
            errors['destination'] = 'Destination is required.'
        
        if not time_out_str:
            errors['time_out'] = 'Time out is required.'
        
        if not return_date_str:
            errors['return_date'] = 'Return date is required.'
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Validation failed.',
                'errors': errors
            }, status=400)
        
        # Parse datetime strings
        from django.utils.dateparse import parse_datetime
        from datetime import datetime
        
        try:
            # Handle datetime-local format (YYYY-MM-DDTHH:MM)
            time_out_str = time_out_str.replace('T', ' ')
            return_date_str = return_date_str.replace('T', ' ')
            
            time_out = datetime.strptime(time_out_str, '%Y-%m-%d %H:%M')
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date/time format. Use YYYY-MM-DDTHH:MM format.',
                'errors': {'datetime': 'Invalid date format.'}
            }, status=400)
        
        # Validate that return date is after time out
        if return_date <= time_out:
            return JsonResponse({
                'success': False,
                'message': 'Return date must be after time out.',
                'errors': {'return_date': 'Return date must be after time out.'}
            }, status=400)
        
        # Create outpass record
        outpass = Outpass.objects.create(
            student=student,
            purpose=purpose,
            reason=purpose,  # Store purpose in reason as well for compatibility
            destination=destination,
            departure_date=time_out,
            time_out=time_out,  # Alias field
            return_date=return_date,
            image=image,
            status='pending',
            hostel_status='inside',
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Outpass request created successfully!',
            'outpass_id': outpass.id,
            'status': outpass.status,
            'data': {
                'purpose': outpass.purpose,
                'destination': outpass.destination,
                'time_out': time_out.strftime('%Y-%m-%d %H:%M'),
                'return_date': return_date.strftime('%Y-%m-%d %H:%M'),
                'status': outpass.get_status_display(),
                'created_at': outpass.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

