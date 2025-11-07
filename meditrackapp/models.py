from django.db import models


# Create your models here.
class Admin(models.Model):
    username=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    
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