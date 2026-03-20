"""
Forms for the Hostel Lock System (Outpass App)
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Outpass, Student


class StudentRegistrationForm(UserCreationForm):
    """Form for student registration"""
    email = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=20, required=True)
    room_number = forms.CharField(max_length=10, required=True)
    hostel_name = forms.CharField(max_length=50, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    parent_phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            student = Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                room_number=self.cleaned_data['room_number'],
                hostel_name=self.cleaned_data['hostel_name'],
                phone_number=self.cleaned_data['phone_number'],
                parent_phone=self.cleaned_data['parent_phone']
            )
            student.save()
        return user


class OutpassForm(forms.ModelForm):
    """Form for creating outpass requests"""
    class Meta:
        model = Outpass
        fields = ['destination', 'reason', 'departure_date', 'return_date']
        widgets = {
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter destination'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Reason for outpass'}),
            'departure_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'return_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        
        if departure and return_date:
            if return_date <= departure:
                raise forms.ValidationError("Return date must be after departure date!")
        
        return cleaned_data

