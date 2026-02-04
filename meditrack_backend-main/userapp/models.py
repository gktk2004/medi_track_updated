from django.db import models
from meditrackapp.models import *
# from meditrackapp.models import *
# from meditrackapp.models import Doctor

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

    TIME_SLOT_CHOICES = [
        ('morning', 'Morning (06:00 - 14:00)'),
        ('evening', 'Evening (14:00 - 22:00)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey("meditrackapp.Doctor", on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, default='morning')
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


class Feedback(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback')
    star_rating = models.IntegerField()
    doctor_interaction_rating = models.FloatField()
    hospital_service_rating = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Appointment #{self.appointment.id} ({self.star_rating} ⭐)"


class BloodDonor(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]
    
    Location_Choices=[
        ('Thrissur','thrissur'),
        ('Ernakulam','ernankulam'),
        ('Palakkad','palakkad'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blood_donor_profile")
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    location= models.CharField(max_length=100, choices=Location_Choices)
    last_donation_date = models.DateField(null=True, blank=True)
    next_donation_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 70.50
    under_medication = models.BooleanField(default=False)
    had_recent_illness = models.BooleanField(default=False)
    illness_details = models.TextField(blank=True)  # optional; only required when had_recent_illness==True
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user",)  # ensures one donor record per user (optional)

    def __str__(self):
        return f"Donor: {self.user_id} ({self.blood_group})"
    
    
class DonationRecord(models.Model):
    DONATION_TYPES = [
        ('Whole Blood', 'Whole Blood'),
        ('Red Cells', 'Red Cells'),
        ('Plasma', 'Plasma'),
        ('Platelets', 'Platelets'),
    ]

    donor = models.ForeignKey(BloodDonor, on_delete=models.CASCADE, related_name="donation_records")
    donation_date = models.DateField()
    location = models.CharField(max_length=200)
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES)
    units = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.user.username} - {self.donation_type} ({self.donation_date})"
    

class DonorAcceptance(models.Model):
    donor = models.ForeignKey(BloodDonor, on_delete=models.CASCADE)
    request = models.ForeignKey("meditrackapp.BloodRequest", on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('accepted', 'Accepted'), ('completed', 'Completed')],
        default='accepted'
    )

    def __str__(self):
        return f"{self.donor.user.username} → {self.request.id} ({self.status})"
    
    
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Complaint #{self.id}"


class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint,related_name="images",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="complaints/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Complaint #{self.complaint.id}"
