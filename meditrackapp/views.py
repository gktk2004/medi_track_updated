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
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
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
    # assuming doctor logs in and their id is stored in session
    doctor_id = request.session.get('doctor_id')

    if not doctor_id:
        return redirect('login')  # redirect if no doctor logged in

    doctor = get_object_or_404(Doctor, id=doctor_id)

    return render(request, 'doctor/doctor_index.html', {'doctor': doctor})


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
    today = timezone.now().date()

    # ✅ Get the logged-in doctor's ID (from session or request.user)
    doctor_id = request.session.get('doctor_id')  # assuming you store this after login

    if not doctor_id:
        return redirect('login')  # or handle unauthorized access

    doctor = get_object_or_404(Doctor, id=doctor_id)

    # ✅ Filter only this doctor's appointments
    appointments = Appointment.objects.filter(
        doctor=doctor,
        status='upcoming',
        date__gte=today
    ).order_by('date', 'token_number')

    return render(request, 'doctor/upcoming_appointments.html', {
        'appointments': appointments,
        'doctor': doctor
    })


def start_op(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    today = datetime.today().date()

    if request.method == "POST":
        # Toggle OP status
        if doctor.op_active:
            doctor.op_active = False
            doctor.save()
            messages.success(request, "OP closed successfully.")
            return redirect("doctor_index")

        # Start OP
        doctor.op_active = True
        doctor.save()

        # Get all today's upcoming appointments
        appointments = Appointment.objects.filter(
            doctor=doctor, date=today, status="upcoming"
        ).order_by("created_at")

        if not appointments.exists():
            messages.warning(request, "No upcoming appointments found for today.")
            return redirect("doctor_index")

        # Add a 15-minute buffer for first token
        BUFFER_MINUTES = 15
        start_time = datetime.now() + timedelta(minutes=BUFFER_MINUTES)

        for i, appointment in enumerate(appointments, start=1):
            appointment.token_number = i
            appointment.save(update_fields=["token_number"])

            expected_time = (start_time + timedelta(minutes=(i - 1) * 10)).time()

            # Build context for HTML email
            context = {
                "user": appointment.user,
                "doctor": doctor,
                "appointment": appointment,
                "expected_time": expected_time.strftime("%I:%M %p"),
                "token_number": i,
            }

            # Subject and content
            subject = "🩺 Your Appointment Schedule for Today"
            text_content = (
                f"Dear {appointment.user.username},\n"
                f"Your appointment with Dr. {doctor.name} is scheduled for today.\n"
                f"Token Number: {i}\n"
                f"Expected Time: {expected_time.strftime('%I:%M %p')}\n"
                f"Please arrive on time.\n\n"
                f"Thank you,\nMediTrack Team"
            )

            html_content = render_to_string("doctor/appointment_mail.html", context)

            # Send the email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[appointment.user.email],
            )
            email.attach_alternative(html_content, "text/html")

            try:
                email.send(fail_silently=False)
            except Exception as e:
                print("❌ Email sending failed:", e)

        messages.success(request, "✅ OP started and emails sent to all booked users.")
        return redirect("doctor_index")

    return redirect("doctor_index")


def add_prescription(request, appointment_id):
    # ✅ Get appointment record
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        # ✅ Extract main form data
        symptoms = request.POST.get('symptoms')
        notes = request.POST.get('notes')

        # ✅ Create the Prescription record
        prescription = Prescription.objects.create(
            appointment=appointment,
            symptoms=symptoms,
            notes=notes,
        )

        # ✅ Collect all medicines fields
        med_names = request.POST.getlist('medicine_name')
        dosages = request.POST.getlist('dosage')
        frequencies = request.POST.getlist('frequency')
        food_instructions = request.POST.getlist('food_instruction')
        days = request.POST.getlist('number_of_days')

        # ✅ Loop through medicines dynamically
        for i in range(len(med_names)):
            # Fetch time_of_day for this medicine only
            times = request.POST.getlist(f'time_of_day_{i+1}')

            # ✅ Create each Medicine record
            Medicine.objects.create(
                prescription=prescription,
                name=med_names[i],
                dosage=dosages[i],
                frequency=frequencies[i],
                time_of_day=times,  # MultiSelectField accepts list
                food_instruction=food_instructions[i],
                number_of_days=days[i],
            )

        # ✅ Update appointment status
        appointment.status = "completed"
        appointment.save()

        messages.success(request, "Prescription added successfully!")
        return redirect("upcoming_appointments")

    # ✅ GET request — render form
    return render(request, "doctor/add_prescription.html", {
        "appointment": appointment
    })