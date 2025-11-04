from django.db import models
from meditrackapp.models import *

# Create your models here.
class User(models.Model):
    username=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    address= models.CharField(max_length=100,default="")
    password=models.CharField(max_length=100)
    phone=models.CharField(max_length=20,default="")
    image=models.ImageField(upload_to="user_image", null=True, blank=True)
    gender=models.CharField(max_length=100)
    birth_date=models.DateField(null=True, blank=True)
    blood_group=models.CharField(max_length=100)
    
    
class Appointment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    token_number = models.PositiveIntegerField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    rescheduled_date = models.DateField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment #{self.id} - {self.user.username} with {self.doctor.name}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)  # MM/YYYY
    cvv = models.CharField(max_length=4, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment.id}"
