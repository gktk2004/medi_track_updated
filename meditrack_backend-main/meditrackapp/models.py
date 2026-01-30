from django.db import models
from userapp.models import *
from userapp.models import User,BloodDonor



# Create your models here.
class Admin(models.Model):
    username=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    
class BloodDonationAdmin(models.Model):
    """
    Dedicated admin for blood donation and blood bank management
    """
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    hospital_name = models.CharField(max_length=150, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Blood Donation Admin - {self.username}"
    
class Department(models.Model):
    department = models.CharField(max_length=150)
    

from multiselectfield import MultiSelectField
class Doctor(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    name = models.CharField(max_length=100, default='')
    phone_number = models.CharField(max_length=15, default='')
    specialization = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    qualification = models.CharField(max_length=150, default='')
    experience = models.CharField(max_length=1000, default='')
    email = models.EmailField()
    password = models.CharField(max_length=100, default='')
    utype = models.CharField(max_length=10, default='doctor')
    status = models.CharField(max_length=20, default='pending')
    image = models.ImageField(upload_to='doctors', null=True, blank=True)
    id_image = models.ImageField(upload_to='doctors_id', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    working_days = MultiSelectField(choices=DAYS_OF_WEEK, max_length=100, blank=True)
    op_active = models.BooleanField(default=False)  # <-- Add this
    


from userapp.models import Appointment

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    symptoms = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for Appointment #{self.appointment.id}"


class Medicine(models.Model):
    TIME_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    FOOD_CHOICES = [
        ('before_food', 'Before Food'),
        ('after_food', 'After Food'),
    ]

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    frequency = models.PositiveIntegerField(default=1, help_text="Number of times per day")
    time_of_day = MultiSelectField(choices=TIME_CHOICES, max_length=100)
    food_instruction = models.CharField(max_length=20, choices=FOOD_CHOICES)
    number_of_days = models.PositiveIntegerField(default=1)
    dosage = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1 tablet, 5 ml, etc.")
    
    
class RescheduleRequest(models.Model):

    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
    ]

    TIME_SLOT_CHOICES = [
        ('morning', 'Morning (06:00 - 14:00)'),
        ('evening', 'Evening (14:00 - 22:00)'),
        ('all_day', 'All Day'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    # ⭐ Doctor chooses WHICH date's appointments to reschedule
    appointment_date = models.DateField(null=True, blank=True)

    token_start = models.PositiveIntegerField()
    token_end = models.PositiveIntegerField()
    
    # ⭐ NEW: Which time slot(s) to reschedule
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, default='all_day')

    reason = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    
    # ⭐ NEW: Store the rescheduled date
    rescheduled_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reschedule Request #{self.id} (Doctor: {self.doctor.name})"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('blood', 'Blood Donation'),
        ('reschedule', 'Reschedule Request'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # or your User model
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='blood')
    # is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.username} - {self.title}"
    


class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    DONATION_TYPES = [
        ('Whole Blood', 'Whole Blood'),
        ('Red Cells', 'Red Cells'),
        ('Plasma', 'Plasma'),
        ('Platelets', 'Platelets'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodDonor.BLOOD_GROUP_CHOICES)
    units_required = models.IntegerField()
    donation_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default='Whole Blood')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=100)  # hospital location
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} - {self.blood_group}"