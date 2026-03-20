"""
Admin configuration for outpass app
"""
from django.contrib import admin
from .models import Student, Outpass, Warden, StudentStatus


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'room_number', 'hostel_name', 'phone_number', 'status']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']
    list_filter = ['hostel_name', 'status']


@admin.register(Outpass)
class OutpassAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'destination', 'departure_date', 'return_date', 'status', 'hostel_status', 'created_at']
    list_filter = ['status', 'hostel_status', 'created_at']
    search_fields = ['student__user__username', 'student__student_id', 'destination']
    actions = ['approve_outpasses', 'reject_outpasses']
    
    def approve_outpasses(self, request, queryset):
        for outpass in queryset.select_related('student'):
            outpass.status = 'approved'
            outpass.hostel_status = 'outside'
            outpass.student.status = StudentStatus.OUTSIDE
            outpass.student.save(update_fields=['status'])
            outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
    approve_outpasses.short_description = "Approve selected outpasses"
    
    def reject_outpasses(self, request, queryset):
        for outpass in queryset.select_related('student'):
            outpass.status = 'rejected'
            outpass.hostel_status = 'inside'
            outpass.student.status = StudentStatus.INSIDE
            outpass.student.save(update_fields=['status'])
            outpass.save(update_fields=['status', 'hostel_status', 'updated_at'])
    reject_outpasses.short_description = "Reject selected outpasses"


@admin.register(Warden)
class WardenAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'designation', 'hostel_name']
    search_fields = ['employee_id', 'user__username', 'user__first_name']

