from django.contrib import admin
from django.urls import path, include
from outpass import views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # =======================
    # REST API Endpoints - Authentication
    # =======================
    path('api/login/', views.login_api_view, name='login_api'),
    path('api/logout/', views.logout_api_view, name='logout_api'),
    path('api/csrf-token/', views.get_csrf_token, name='csrf_token'),
    
    # =======================
    # REST API Endpoints - Student Features
    # =======================
    path('api/create-outpass/', views.create_outpass_api, name='create_outpass_api'),
    path('api/my-outpasses/', views.my_outpasses_api, name='my_outpasses_api'),
    path('api/mark-in/', views.mark_in_api, name='mark_in_api'),
    
    # =======================
    # REST API Endpoints - Admin Features
    # =======================
    path('api/admin/dashboard/', views.admin_dashboard_stats_api, name='admin_dashboard_stats_api'),
    path('api/admin/dashboard/stats/', views.admin_dashboard_stats_api, name='admin_dashboard_stats_api'),
    path('api/admin/dashboard/stats-complete/', views.admin_dashboard_complete_stats_api, name='admin_dashboard_complete_stats_api'),
    path('api/admin/outpasses/', views.get_outpasses_api, name='get_outpasses_api'),
    path('api/admin/approve/<int:outpass_id>/', views.approve_outpass_api, name='approve_outpass_api'),
    path('api/admin/reject/<int:outpass_id>/', views.reject_outpass_api, name='reject_outpass_api'),
    
    # =======================
    # REST API Endpoints - Actions
    # =======================
    path('api/mark-student-status/', views.mark_student_status, name='mark_student_status'),
    path('api/update-outpass-status/', views.update_outpass_status, name='update_outpass_status'),
    
    # =======================
    # REST API Endpoints - Charts
    # =======================
    path('api/chart/daily-requests/', views.get_daily_requests_chart, name='get_daily_requests_chart'),
    path('api/chart/hostel-status/', views.get_hostel_status_chart, name='get_hostel_status_chart'),
    path('api/chart/student-movement/', views.get_student_movement_api, name='get_student_movement_api'),
    path('api/admin/occupancy-percentage/', views.get_occupancy_percentage_api, name='get_occupancy_percentage_api'),
    
    # =======================
    # REST API Endpoints - Student Management
    # =======================
    path('api/admin/students/', views.get_all_students_api, name='get_all_students_api'),
    path('api/admin/students/create/', views.create_student_api, name='create_student_api'),
    path('api/admin/students/<int:student_id>/', views.get_student_api, name='get_student_api'),
    path('api/admin/students/<int:student_id>/update/', views.update_student_api, name='update_student_api'),
    path('api/admin/students/<int:student_id>/delete/', views.delete_student_api, name='delete_student_api'),
    path('api/admin/students/<int:student_id>/reset-password/', views.reset_student_password_api, name='reset_student_password_api'),
    
    # =======================
    # Frontend Routes
    # =======================
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student-dashboard/', views.dashboard, name='student_dashboard'),
    path('create-pass/', views.create_pass, name='create_pass'),
    path('create-pass-api/', views.create_pass_api_view, name='create_pass_api'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:outpass_id>/', views.approve_outpass, name='approve_outpass'),
    path('reject/<int:outpass_id>/', views.reject_outpass, name='reject_outpass'),
]

