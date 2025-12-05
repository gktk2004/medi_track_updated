from .models import *
from meditrackapp.models import *
from rest_framework import serializers
from datetime import date


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
    department_name = serializers.CharField(source='doctor.specialization.department', read_only=True)
    class Meta:
        model = Appointment
        fields = [
            'id',
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
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_image= serializers.ImageField(source='doctor.image',read_only=True)
    department_name = serializers.CharField(source='doctor.specialization.department', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor_id',
            'user_name',
            'doctor_name',
            'doctor_image',
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
        
        
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            "name", "dosage", "frequency", "time_of_day",
            "food_instruction", "number_of_days"
        ]

class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='appointment.doctor.name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.date', read_only=True)
    medicines = MedicineSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id", "doctor_name", "appointment_date",
            "symptoms", "notes", "created_at", "medicines"
        ]
        
        
class BloodDonorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True, required=True)  # accept user id in request

    class Meta:
        model = BloodDonor
        fields = [
            "id",
            "user_id",
            "blood_group",
            "location",
            "last_donation_date",
            "weight",
            "under_medication",
            "had_recent_illness",
            "illness_details",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_last_donation_date(self, value):
        # Must not be in the future
        if value and value > date.today():
            raise serializers.ValidationError("Last donation date cannot be in the future.")
        return value

    def validate_weight(self, value):
        # Example threshold: minimum 50 kg (adjust to local policy)
        if value <= 0:
            raise serializers.ValidationError("Weight must be a positive number.")
        if value < 50:
            raise serializers.ValidationError("Weight must be at least 50 kg to donate (adjust policy as needed).")
        return value

    def validate(self, attrs):
        had_recent = attrs.get("had_recent_illness")
        illness_details = attrs.get("illness_details", "").strip()

        # If user had recent illness, details should be provided
        if had_recent and not illness_details:
            raise serializers.ValidationError({"illness_details": "Provide details of recent illness."})

        # If user did not have recent illness but provided details, accept but trim
        return attrs

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")

        # Import your custom user model
        from userapp.models import User

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User does not exist in userapp.User"})

        donor, created = BloodDonor.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return donor
    
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "type","message", "created_at"]
        
        
class BloodRequestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)

    class Meta:
        model = BloodRequest
        fields = [
            'id',
            'doctor',
            'doctor_name',
            'blood_group',
            'units_required',
            'donation_date',
            'donation_type',    
            'location',
            'reason',
            'status',
            'created_at'
        ]
