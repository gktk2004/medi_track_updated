from .models import *
from meditrackapp.models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_email(self, value):
        """Ensure the email is unique."""
        # Check if another user already has this email
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','password']
        

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        
        
class DoctorSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'qualification', 'experience', 'email',
            'phone_number', 'image', 'specialization_name'
        ]
        
class AppointmentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"
        
        
class AppointmentListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor_name',
            'date',
            'token_number',
            'symptoms',
            'payment_status',
            'status',
            'rescheduled_date',
            'cancellation_reason',
            'created_at',
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    department_name = serializers.CharField(source='doctor.specialization', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'user_name',
            'doctor_name',
            'department_name',
            'date',
            'token_number',
            'symptoms',
            'payment_status',
            'status',
            'rescheduled_date',
            'cancellation_reason',
            'created_at',
            'updated_at',
        ]