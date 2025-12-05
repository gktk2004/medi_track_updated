from django.shortcuts import render
from datetime import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from .models import *
from userapp.models import *
from django.db.models import Q
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.utils.timezone import now

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
    doctors = Doctor.objects.filter(status='pending').order_by('-id')  # only pending doctors
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
    return redirect(request.META.get("HTTP_REFERER", "/"))  # Redirect back to the doctor list

def reject_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = False
    doctor.status = 'rejected'
    doctor.save()
    messages.success(request, f"Doctor {doctor.name} has been rejected.")
    return redirect(request.META.get("HTTP_REFERER", "/"))  # Redirect back to the doctor list


def view_approved_doctors(request):
    doctors = Doctor.objects.filter(is_approved=True)
    return render(request, 'admin/view_approved_doctors.html', {'doctors': doctors})\
        
def view_rejected_doctors(request):
    doctors = Doctor.objects.filter(is_approved=False)
    return render(request, 'admin/view_rejected_doctors.html', {'doctors': doctors})


from django.utils import timezone
from datetime import datetime
# def doctor_upcoming_appointments(request):
#     today = timezone.now().date()

#     # ✅ Get the logged-in doctor's ID (from session or request.user)
#     doctor_id = request.session.get('doctor_id')  # assuming you store this after login

#     if not doctor_id:
#         return redirect('login')  # or handle unauthorized access

#     doctor = get_object_or_404(Doctor, id=doctor_id)

#     # ✅ Filter only this doctor's appointments
#     appointments = Appointment.objects.filter(
#         doctor=doctor,
#         status='upcoming',
#         date__gte=today
#     ).order_by('date', 'token_number')

#     return render(request, 'doctor/upcoming_appointments.html', {
#         'appointments': appointments,
#         'doctor': doctor
#     })


def doctor_ongoing_appointments(request):
    # Use localdate() so timezone settings are respected
    today = timezone.localdate()

    # Get logged-in doctor's ID from session (same as your original approach)
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('login')

    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Filter: only appointments for this doctor that are scheduled for today
    appointments = Appointment.objects.filter(
        doctor=doctor,
        status='upcoming',
        date__exact=today
    ).order_by('date', 'token_number')

    return render(request, 'doctor/ongoing_appointments.html', {
        'appointments': appointments,
        'doctor': doctor,
        'today': today
    })


def doctor_appointment_history(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    search = request.GET.get("search", "").strip()
    date = request.GET.get("date", "").strip()
    status = request.GET.get("status", "").strip()  # completed, cancelled, rescheduled

    # Only show meaningful past appointments
    allowed_status = ["completed", "cancelled", "rescheduled"]

    appointments = Appointment.objects.filter(
        doctor=doctor,
        status__in=allowed_status
    ).select_related("user")

    # Search filter (patient name / email / phone)
    if search:
        appointments = appointments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__phone__icontains=search)
        )

    # Date filter
    if date:
        appointments = appointments.filter(date=date)

    # Status filter
    if status:
        appointments = appointments.filter(status=status)

    # Order newest → oldest
    appointments = appointments.order_by("-date", "-id")

    return render(request, "doctor/doctor_appointment_history.html", {
        "doctor": doctor,
        "appointments": appointments,
    })

def upcoming_appointments(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get filters
    search = request.GET.get("search", "").strip()
    date = request.GET.get("date", "").strip()

    # Base Query: Only upcoming appointments
    appointments = Appointment.objects.filter(
        doctor=doctor,
        status="upcoming"
    ).select_related("user")

    # Search filter (patient name, email, phone)
    if search:
        appointments = appointments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__phone__icontains=search)
        )

    # Date filter
    if date:
        appointments = appointments.filter(date=date)

    # Order by date and token_number
    appointments = appointments.order_by("date", "token_number")

    return render(request, "doctor/doctor_upcoming_appointments.html", {
        "doctor": doctor,
        "appointments": appointments,
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
    
    
# def doctor_patients_view(request, doctor_id):
#     """
#     Doctor can view and search their patients' completed appointment medical history.
#     """
#     doctor = get_object_or_404(Doctor, id=doctor_id)
#     search_query = request.GET.get('search', '').strip()

#     # ✅ Filter only completed appointments
#     appointments = (
#         Appointment.objects.filter(doctor=doctor, status='completed')
#         .select_related('user')
#         .prefetch_related('prescription__medicines')
#         .order_by('-date')
#     )

#     # ✅ Apply search filter (by patient name, email, or phone)
#     if search_query:
#         appointments = appointments.filter(
#             Q(user__username__icontains=search_query) |
#             Q(user__email__icontains=search_query) |
#             Q(user__phone__icontains=search_query)
#         )

#     # ✅ Group data by patient
#     patient_data = {}
#     for appointment in appointments:
#         patient = appointment.user
#         if patient not in patient_data:
#             patient_data[patient] = []
#         prescription = getattr(appointment, 'prescription', None)
#         patient_data[patient].append({
#             'appointment': appointment,
#             'prescription': prescription,
#             'medicines': prescription.medicines.all() if prescription else [],
#         })

#     # ✅ Remove patients without any completed appointments
#     patient_data = {p: r for p, r in patient_data.items() if r}

#     return render(request, 'doctor/doctor_patients.html', {
#         'doctor': doctor,
#         'patient_data': patient_data,
#         'search_query': search_query,
#     })
    

def doctor_patients_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    search_query = request.GET.get("search", "").strip()

    # STEP 1: Patients who visited THIS doctor
    my_patients = Appointment.objects.filter(
        doctor=doctor,
        status="completed"
    ).values_list("user_id", flat=True).distinct()

    # STEP 2: Apply search correctly (fixed Q syntax)
    if search_query:
        my_patients = User.objects.filter(
            Q(id__in=my_patients) &
            (
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        ).values_list("id", flat=True)

    # STEP 3: Get ALL completed appointments of these patients
    appointments = (
        Appointment.objects.filter(
            user_id__in=my_patients,
            status="completed"
        )
        .select_related("user", "doctor")
        .prefetch_related("prescription__medicines")
        .order_by("-date")
    )

    # STEP 4: Group by patients
    patient_data = {}
    for appt in appointments:
        patient = appt.user
        if patient not in patient_data:
            patient_data[patient] = []

        prescription = getattr(appt, "prescription", None)

        patient_data[patient].append({
            "appointment": appt,
            "prescription": prescription,
            "medicines": prescription.medicines.all() if prescription else [],
            "doctor": appt.doctor,  # Important: show which doctor treated
        })

    return render(request, "doctor/doctor_patients.html", {
        "doctor": doctor,
        "patient_data": patient_data,
        "search_query": search_query,
    })

def doctor_feedback_view(request, doctor_id):
    """
    Display all feedbacks given to a specific doctor
    (based on appointments linked to that doctor).
    """
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # ✅ Filter feedbacks by appointment's doctor
    feedback_list = Feedback.objects.filter(appointment__doctor=doctor).select_related('appointment__user')

    return render(request, 'doctor/doctor_feedback.html', {
        'doctor': doctor,
        'feedback_list': feedback_list,
    })
    

# def admin_token_status(request):
#     today = now().date()
#     token_data = []

#     doctors = Doctor.objects.all()

#     for doctor in doctors:
#         # All today's appointments for the doctor
#         appointments = Appointment.objects.filter(
#             doctor=doctor,
#             date=today
#         ).order_by("token_number")

#         # Skip doctors with no appointments
#         if not appointments.exists():
#             continue

#         total_tokens = appointments.count()

#         # Find current token (first upcoming appointment)
#         current_app = appointments.filter(status="upcoming").order_by("token_number").first()
#         current_token = current_app.token_number if current_app else None

#         # Determine OP status
#         status_label = "running" if current_app else "completed"

#         token_data.append({
#             "doctor": doctor,
#             "department": doctor.specialization.department if doctor.specialization else "",
#             "current_token": current_token,
#             "total_tokens": total_tokens,
#             "status": status_label,
#         })

#     return render(request, "admin/admin_token_status.html", {"token_data": token_data})


def admin_token_status(request):
    today = now().date()
    token_data = []

    doctors = Doctor.objects.all()

    for doctor in doctors:
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today,
            payment_status="completed",
        ).exclude(status__in=["cancelled", "rescheduled"]).order_by("token_number")

        if not appointments.exists():
            continue

        total_tokens = appointments.count()

        current_app = appointments.filter(
            status__in=["upcoming", "in-progress"]
        ).order_by("token_number").first()

        current_token = current_app.token_number if current_app else None
        status_label = "running" if current_app else "completed"

        token_data.append({
            "doctor": doctor,
            "department": doctor.specialization.department if doctor.specialization else "",
            "current_token": current_token,
            "total_tokens": total_tokens,
            "status": status_label,
        })

    return render(request, "admin/admin_token_status.html", {"token_data": token_data})



# def admin_doctor_queue(request, doctor_id):
#     today = now().date()

#     doctor = get_object_or_404(Doctor, id=doctor_id)

#     appointments = Appointment.objects.filter(
#         doctor=doctor,
#         date=today
#     ).order_by("token_number")

#     return render(request, "admin/admin_doctor_queue.html", {
#         "doctor": doctor,
#         "appointments": appointments
#     })

def admin_doctor_queue(request, doctor_id):
    today = now().date()

    doctor = get_object_or_404(Doctor, id=doctor_id)

    appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today,
        payment_status="completed",
        status__in=["upcoming", "in-progress"]   # ONLY valid queue items
    ).exclude(status__in=["cancelled", "rescheduled"]).order_by("token_number")

    return render(request, "admin/admin_doctor_queue.html", {
        "doctor": doctor,
        "appointments": appointments
    })


# def admin_doctor_queue(request, doctor_id):
#     today = now().date()

#     doctor = get_object_or_404(Doctor, id=doctor_id)

#     appointments = Appointment.objects.filter(
#         doctor=doctor,
#         date=today
#     ).order_by('token_number')

#     return render(request, "admin/admin_doctor_queue.html", {
#         "doctor": doctor,
#         "appointments": appointments
#     })
    
    
def admin_reports(request):

    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    appointments = Appointment.objects.all()
    feedbacks = Feedback.objects.all()
    donation_records = DonationRecord.objects.all()
    blood_requests = BloodRequest.objects.all()
    donor_acceptances = DonorAcceptance.objects.all()

    # Apply Date Filter
    if from_date and to_date:
        appointments = appointments.filter(date__range=[from_date, to_date])
        feedbacks = feedbacks.filter(created_at__date__range=[from_date, to_date])
        donation_records = donation_records.filter(donation_date__range=[from_date, to_date])
        blood_requests = blood_requests.filter(created_at__date__range=[from_date, to_date])
        donor_acceptances = donor_acceptances.filter(accepted_at__date__range=[from_date, to_date])

    context = {
        "total_appointments": Appointment.objects.count(),
        "total_feedbacks": Feedback.objects.count(),
        "total_doctors": Doctor.objects.filter(is_approved=True).count(),

        # Report Lists
        "appointment_list": appointments,
        "feedback_list": feedbacks,
        "donation_records": donation_records,
        "blood_requests": blood_requests,
        "donor_acceptances": donor_acceptances,
    }

    return render(request, "admin/reports.html", context)


def doctor_reschedule_request(request):
    doctor_id = request.session.get("doctor_id")
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == "POST":
        appointment_date = request.POST.get("appointment_date")

        token_start = int(request.POST['token_start'])
        token_end = int(request.POST['token_end'])
        reason = request.POST.get('reason', '')

        RescheduleRequest.objects.create(
            doctor=doctor,
            appointment_date=appointment_date,   # ⭐ Save selected date
            token_start=token_start,
            token_end=token_end,
            reason=reason
        )

        return redirect('doctor_reschedule_request')

    return render(request, 'doctor/reschedule_request.html')

from django.utils import timezone
# import datetime   # DO NOT REMOVE OR CHANGE
import datetime as dt   # SAFE VERSION


def admin_reschedule_request_list(request):

    # only admin check
    if request.session.get("admin_id") is None:
        return redirect("admin_login")

    requests = RescheduleRequest.objects.all().order_by('-id')

    return render(request, 'admin/reschedule_request_list.html', {
        "requests": requests
    })
    
    
# def admin_review_reschedule(request, req_id):
#     # admin auth (session)
#     if request.session.get("admin_id") is None:
#         return redirect("admin_login")

#     rr = get_object_or_404(RescheduleRequest, id=req_id)
#     doctor = rr.doctor

#     # map weekday index -> name used in doctor.working_days
#     DAYS_MAP = {
#         0: "monday",
#         1: "tuesday",
#         2: "wednesday",
#         3: "thursday",
#         4: "friday",
#         5: "saturday",
#         6: "sunday",
#     }

#     def get_next_working_day_after(start_date, doctor):
#         """
#         Find the next date after start_date (exclusive) when doctor.working_days includes that weekday.
#         start_date must be a date object.
#         """
#         # search up to 4 weeks to be safe
#         for i in range(1, 29):
#             candidate = start_date + datetime.timedelta(days=i)
#             weekday_name = DAYS_MAP[candidate.weekday()]
#             if weekday_name in doctor.working_days:
#                 return candidate
#         # fallback: return start_date + 1 day
#         return start_date + datetime.timedelta(days=1)

#     # Determine base date to search from: appointment_date if present, else today
#     if rr.appointment_date:
#         base = rr.appointment_date
#     else:
#         base = timezone.localdate()

#     # compute proposed new reschedule date (next working day after base + 5 days)
#     proposed_next_working = get_next_working_day_after(base, doctor)
#     proposed_reschedule_date = proposed_next_working + datetime.timedelta(days=5)

#     # If form posted: handle approve/reject
#     if request.method == "POST" and rr.status == "pending":
#         action = request.POST.get("action")
#         admin_note = request.POST.get("admin_note", "")

#         if action == "reject":
#             rr.status = "rejected"
#             rr.admin_note = admin_note
#             rr.processed_at = timezone.now()
#             rr.save()
#             return redirect("admin_reschedule_request_list")

#         if action == "approve":
#             # Update appointments that match doctor's appointment_date and token range
#             appointments = Appointment.objects.filter(
#                 doctor=doctor,
#                 date=rr.appointment_date,
#                 token_number__gte=rr.token_start,
#                 token_number__lte=rr.token_end,
#                 status="upcoming",
#             )

#             for appt in appointments:
#                 appt.status = "rescheduled"
#                 appt.rescheduled_date = proposed_reschedule_date
#                 appt.save()

#             rr.status = "approved"
#             rr.admin_note = admin_note
#             rr.rescheduled_date = proposed_reschedule_date  # optional to store
#             rr.processed_at = timezone.now()
#             rr.save()

#             return redirect("admin_reschedule_request_list")

#     # render page — show rr and proposed_reschedule_date
#     return render(request, "admin/reschedule_review.html", {
#         "rr": rr,
#         "proposed_reschedule_date": proposed_reschedule_date,
#         "proposed_next_working": proposed_next_working,
#     })


# -------------------------
# 🔔 Notification Function
# -------------------------
def create_reschedule_notification(user, doctor, old_date, new_date, token_number, reason):
    title = "Appointment Rescheduled"

    message = (
        f"Your appointment with Dr. {doctor.name} originally on {old_date} "
        f"(Token #{token_number}) has been rescheduled to {new_date}.\n"
        f"Reason: {reason or 'Not provided'}"
    )

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type="reschedule"   # ⭐ NEW FIELD ADDED
    )



# -------------------------
# 🏥 ADMIN REVIEW RESCHEDULE
# -------------------------
def admin_review_reschedule(request, req_id):

    # Session check
    if request.session.get("admin_id") is None:
        return redirect("admin_login")

    rr = get_object_or_404(RescheduleRequest, id=req_id)
    doctor = rr.doctor

    # Map weekday number to readable string
    DAYS_MAP = {
        0: "monday",
        1: "tuesday",
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday",
    }

    # Function to find next working day
    def get_next_working_day_after(start_date, doctor):
        for i in range(1, 29):
            candidate = start_date + dt.timedelta(days=i)
            weekday_name = DAYS_MAP[candidate.weekday()]
            if weekday_name in doctor.working_days:
                return candidate
        return start_date + dt.timedelta(days=1)

    # Base date to search from
    base = rr.appointment_date if rr.appointment_date else timezone.localdate()

    # Auto-calc new proposed reschedule date
    proposed_next_working = get_next_working_day_after(base, doctor)
    proposed_reschedule_date = proposed_next_working + dt.timedelta(days=5)

    # -------------------
    # POST: Approve / Reject
    # -------------------
    if request.method == "POST" and rr.status == "pending":
        action = request.POST.get("action")
        admin_note = request.POST.get("admin_note", "")

        # Reject
        if action == "reject":
            rr.status = "rejected"
            rr.admin_note = admin_note
            rr.processed_at = timezone.now()
            rr.save()
            return redirect("admin_reschedule_request_list")

        # Approve
        if action == "approve":

            appointments = Appointment.objects.filter(
                doctor=doctor,
                date=rr.appointment_date,
                token_number__gte=rr.token_start,
                token_number__lte=rr.token_end,
                status="upcoming",
            )

            for appt in appointments:
                user = appt.user
                old_date = appt.date
                token = appt.token_number

                # Update appointment
                appt.status = "rescheduled"
                appt.rescheduled_date = proposed_reschedule_date
                appt.save()

                # 🔔 Create notification
                create_reschedule_notification(
                    user=user,
                    doctor=doctor,
                    old_date=old_date,
                    new_date=proposed_reschedule_date,
                    token_number=token,
                    reason=rr.reason
                )

            # Update request
            rr.status = "approved"
            rr.admin_note = admin_note
            rr.rescheduled_date = proposed_reschedule_date
            rr.processed_at = timezone.now()
            rr.save()

            return redirect("admin_reschedule_request_list")

    # Render Page
    return render(request, "admin/reschedule_review.html", {
        "rr": rr,
        "proposed_reschedule_date": proposed_reschedule_date,
        "proposed_next_working": proposed_next_working,
    })
    
    
def doctor_blood_request_view(request):

    # 🔐 Check session login
    if 'doctor_id' not in request.session:
        messages.error(request, "Please login to continue.")
        return redirect('login')

    doctor_id = request.session['doctor_id']
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == "POST":
        blood_group = request.POST.get("blood_group")
        units_required = request.POST.get("units_required")
        location = request.POST.get("location")
        donation_type = request.POST.get("donation_type")
        donation_date = request.POST.get("donation_date")   # ⭐ NEW
        reason = request.POST.get("reason")

        # Convert empty date → None
        if donation_date == "":
            donation_date = None

        # Create blood request record
        BloodRequest.objects.create(
            doctor=doctor,
            blood_group=blood_group,
            units_required=units_required,
            location=location,
            donation_type=donation_type,
            donation_date=donation_date,   # ⭐ SAVE NEW FIELD
            reason=reason
        )

        messages.success(request, "Blood request submitted successfully!")
        return redirect("doctor_blood_request")

    return render(request, "doctor/request_blood.html", {"doctor": doctor})




def admin_view_blood_requests(request):
    requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, "admin/blood_requests.html", {"requests": requests})


# def admin_approve_blood_request(request, req_id):
#     req = BloodRequest.objects.get(id=req_id)
#     req.status = "approved"
#     req.save()

#     donors = BloodDonor.objects.filter(
#         blood_group=req.blood_group,
#         location=req.location
#     )

#     for donor in donors:
#         Notification.objects.create(
#             user=donor.user,
#             title="Urgent Blood Needed",
#             message=f"{req.blood_group} blood needed at {req.location}. Please help!"
#         )

#     messages.success(request, "Request Approved and donors notified!")
#     return redirect("admin_blood_requests")

def admin_approve_blood_request(request, req_id):
    try:
        req = BloodRequest.objects.get(id=req_id)
    except BloodRequest.DoesNotExist:
        messages.error(request, "Blood request not found.")
        return redirect("admin_blood_requests")

    # Approve the blood request
    req.status = "approved"
    req.save()

    # Find donors who match the blood group & location
    donors = BloodDonor.objects.filter(
        blood_group=req.blood_group,
        location=req.location
    )

    # Format donation date if available
    donation_date_text = req.donation_date.strftime("%d-%m-%Y") if req.donation_date else "As soon as possible"

    # Create notifications
    for donor in donors:
        Notification.objects.create(
            user=donor.user,
            title="Urgent Blood Donation Needed",
            message=(
                f"Dear Donor, your blood type {req.blood_group} is urgently needed at {req.location}.\n"
                f"➡ Donation Type: {req.donation_type}\n"
                f"➡ Units Required: {req.units_required}\n"
                f"➡ Preferred Donation Date: {donation_date_text}\n"
                f"➡ Reason: {req.reason}\n\n"
                f"Please help if you are available."
            ),
            type="blood"   # ⭐ Added notification category
        )

    messages.success(request, "Blood request approved and donors have been notified!")
    return redirect("admin_blood_requests")

def admin_reject_blood_request(request, req_id):
    req = BloodRequest.objects.get(id=req_id)
    req.status = "rejected"
    req.save()

    messages.warning(request, "Request Rejected!")
    return redirect("admin_blood_requests")


def admin_view_accepted_donors(request, req_id):
    req = get_object_or_404(BloodRequest, id=req_id)
    accepted_donors = DonorAcceptance.objects.filter(request=req)

    return render(request, "admin/accepted_donors.html", {
        "request_obj": req,
        "accepted_donors": accepted_donors
    })
    

def admin_complete_donation(request, accept_id):
    acceptance = get_object_or_404(DonorAcceptance, id=accept_id)

    acceptance.status = "completed"
    acceptance.save()

    donor = acceptance.donor
    req = acceptance.request

    DonationRecord.objects.create(
        donor=donor,
        donation_date=req.donation_date or timezone.now().date(),
        location=req.location,
        donation_type=req.donation_type,
        units=req.units_required
    )

    donor.last_donation_date = req.donation_date or timezone.now().date()
    donor.save()

    messages.success(request, "Donation marked as completed.")
    return redirect("admin_blood_requests")
