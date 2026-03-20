"""
Serializers for the Hostel Lock System (Outpass App)
Django REST Framework serializers for API responses
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Outpass, Warden


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'room_number', 'hostel_name', 
                  'phone_number', 'parent_phone', 'status', 'full_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class OutpassListSerializer(serializers.ModelSerializer):
    """Serializer for Outpass list view"""
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    student_room = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    hostel_status_display = serializers.CharField(source='get_hostel_status_display', read_only=True)
    
    class Meta:
        model = Outpass
        fields = [
            'id', 'student', 'student_name', 'student_id', 'student_room',
            'destination', 'purpose', 'reason',
            'departure_date', 'return_date',
            'status', 'status_display',
            'hostel_status', 'hostel_status_display',
            'image', 'created_at', 'updated_at'
        ]
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    
    def get_student_id(self, obj):
        return obj.student.student_id
    
    def get_student_room(self, obj):
        return obj.student.room_number


class OutpassCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Outpass"""
    time_out = serializers.DateTimeField(required=False)
    return_time = serializers.DateTimeField(required=False)
    
    class Meta:
        model = Outpass
        fields = ['id', 'destination', 'purpose', 'reason', 
                  'departure_date', 'return_date', 'time_out', 'return_time',
                  'image', 'status', 'hostel_status']
    
    def create(self, validated_data):
        # Set status to pending by default
        validated_data['status'] = 'pending'
        validated_data['hostel_status'] = 'inside'
        return super().create(validated_data)


class OutpassDetailSerializer(serializers.ModelSerializer):
    """Serializer for Outpass detail view"""
    student = StudentSerializer(read_only=True)
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    hostel_status_display = serializers.CharField(source='get_hostel_status_display', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Outpass
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'destination', 'purpose', 'reason',
            'departure_date', 'return_date',
            'status', 'status_display',
            'hostel_status', 'hostel_status_display',
            'image', 'image_url',
            'created_at', 'updated_at'
        ]
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    
    def get_student_id(self, obj):
        return obj.student.student_id
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class WardenSerializer(serializers.ModelSerializer):
    """Serializer for Warden model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Warden
        fields = ['id', 'user', 'employee_id', 'designation', 'hostel_name']


class LoginRequestSerializer(serializers.Serializer):
    """Serializer for login request"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    redirect = serializers.CharField(required=False)
    user = serializers.DictField(required=False)


class OutpassActionSerializer(serializers.Serializer):
    """Serializer for outpass action (approve/reject)"""
    outpass_id = serializers.IntegerField(required=True)
    action = serializers.ChoiceField(choices=['approve', 'reject'])


class MarkStatusSerializer(serializers.Serializer):
    """Serializer for marking student status"""
    outpass_id = serializers.IntegerField(required=True)
    hostel_status = serializers.ChoiceField(choices=['inside', 'outside'])


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_students = serializers.IntegerField()
    students_inside = serializers.IntegerField()
    students_outside = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    approved_requests = serializers.IntegerField()
    rejected_requests = serializers.IntegerField()
    total_requests = serializers.IntegerField()

