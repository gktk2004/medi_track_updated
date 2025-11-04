from django.shortcuts import render
from datetime import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.contrib import messages
from .models import *
from userapp.models import *
from django.db.models import Q
from django.db.models import Sum, Count
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.shortcuts import render


# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check if it's a regular user
        admin = Admin.objects.filter(email=email, password=password).first()
        doctor = Doctor.objects.filter(email=email,password=password).first()

        if admin:
            request.session['admin_id'] = admin.id
            request.session['role'] = 'admin'
            messages.success(request, "Admin login successful!")
            return redirect('admin_index')
        
        elif doctor:
            request.session['doctor_id'] = doctor.id
            request.session['role'] = 'doctor'
            messages.success(request, "doctor login successful!")
            return redirect('doctor_index')

        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')

def admin_index(request):
    return render(request,'admin/admin_index.html')


def manage_departments(request):
    departments = Department.objects.all()
    return render(request, 'admin/manage_departments.html', {'departments': departments})

def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('department')
        if name:
            Department.objects.create(department=name)
            messages.success(request, f"Department '{name}' added successfully!")
        else:
            messages.error(request, "Department name cannot be empty.")
        return redirect('manage_departments')
    return redirect('manage_departments')

def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    messages.success(request, f"Department '{dept.department}' deleted successfully!")
    return redirect('manage_departments')


def manage_doctor(request):
    return render(request,'admin/manage_doctor.html')

def add_doctor(request):
    # Fetch all departments to populate the dropdown
    departments = Department.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        password = request.POST.get("password")
        specialization_id = request.POST.get("specialization")
        

        # Check required fields
        if not specialization_id:
            messages.error(request, "Please select a department.")
            return redirect("add_doctor")

        # Create Doctor object
        doctor = Doctor(
            name=name,
            phone_number=phone_number,
            email=email,
            password=password,
            specialization_id=specialization_id,  # assign foreign key
        )
        doctor.save()
        messages.success(request, f"Doctor {name} added successfully!")
        return redirect("manage_doctor")  # redirect to manage page

    return render(request, "admin/add_doctor.html", {"departments": departments})

def view_doctors(request):
    doctors = Doctor.objects.all().order_by('-id')  # latest first
    return render(request, 'admin/view_doctors.html', {'doctors': doctors})


def doctor_index(request):
    return render(request,'doctor/doctor_index.html')


def doctor_profile(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        messages.error(request, "Please login first.")
        return redirect('login')

    doctor = Doctor.objects.get(id=doctor_id)
    return render(request, 'doctor/doctor_profile.html', {'doctor': doctor})


def doctor_update_profile(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        messages.error(request, "Please login first.")
        return redirect('login')

    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == 'POST':
        doctor.qualification = request.POST.get('qualification', doctor.qualification)
        doctor.experience = request.POST.get('experience', doctor.experience)

        if 'image' in request.FILES:
            doctor.image = request.FILES['image']
        if 'id_image' in request.FILES:
            doctor.id_image = request.FILES['id_image']
            
        doctor.working_days = request.POST.getlist('working_days')

        doctor.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('doctor_profile')

    return render(request, 'doctor/doctor_update_profile.html', {'doctor': doctor})


def approve_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = True
    doctor.status = 'approved'
    doctor.save()
    messages.success(request, f"Doctor {doctor.name} has been approved.")
    return redirect('manage_doctor')  # Redirect back to the doctor list

def reject_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = False
    doctor.status = 'rejected'
    doctor.save()
    messages.success(request, f"Doctor {doctor.name} has been rejected.")
    return redirect('manage_doctor')  # Redirect back to the doctor list


def view_approved_doctors(request):
    doctors = Doctor.objects.filter(is_approved=True)
    return render(request, 'admin/view_approved_doctors.html', {'doctors': doctors})\
        
def view_rejected_doctors(request):
    doctors = Doctor.objects.filter(is_approved=False)
    return render(request, 'admin/view_rejected_doctors.html', {'doctors': doctors})


from django.utils import timezone
from datetime import datetime
def doctor_upcoming_appointments(request):
    today = timezone.now().date()  # ✅ this works correctly
    appointments = Appointment.objects.filter(
        status='upcoming',
        date__gte=today
    ).order_by('date', 'token_number')

    return render(request, 'doctor/upcoming_appointments.html', {
        'appointments': appointments
    })
