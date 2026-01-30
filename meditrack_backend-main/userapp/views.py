from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Q
from .models import *
from meditrackapp.models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status,viewsets,generics
from rest_framework.views import APIView
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
from django.db.models import Max
from rest_framework import status as http_status
import datetime 
from rest_framework.generics import ListAPIView


# Create your views here.
# class UserRegistrationView(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     http_method_names = ['post']
    
#     def create(self, request, *args, **kwargs):
#         serializer =self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             response_data = {
#                 "status":"success",
#                 "message" : "User Created Successfully",
#                 "data" : serializer.data
#             }
#             return Response(response_data, status=status.HTTP_201_CREATED)
#         else:
#             response_data = {
#                 "status":"failed",
#                 "message": "Invalid Details",
#                 "errors": serializer.errors,
#                 "data": request.data
#             }
#             return Response(response_data,status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        if request.content_type.startswith('application/json'):
            return Response(
                {"error": "Please upload data as multipart/form-data when including files."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "User Created Successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "failed",
            "message": "Invalid Details",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserLoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             email = request.data.get("email")
#             password = request.data.get("password")
            
#             try:
#                 user = User.objects.get(email=email)
#                 if password == user.password:
#                     response_data = {
#                         "status": "success",
#                         "message": "User logged in successfully",
#                         "user_id": str(user.id),
#                         "data": request.data
#                     }
#                     request.session['id'] = user.id
#                     return Response(response_data, status=status.HTTP_200_OK)
#                 else:
#                     return Response({
#                         "status": "failed",
#                         "message": "Invalid credentials",
#                         "data": request.data
#                     }, status=status.HTTP_400_BAD_REQUEST)

#             except User.DoesNotExist:
#                 return Response({
#                     "status": "failed",
#                     "message": "User not found",
#                     "data": request.data
#                 }, status=status.HTTP_400_BAD_REQUEST)
                
#         return Response({
#             "status": "failed",
#             "message": "Invalid input",
#             "errors": serializer.errors,
#             "data": request.data
#         }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = request.data.get("email")
            password = request.data.get("password")
            
            try:
                user = User.objects.get(email=email)

                if password == user.password:

                    # Check if donor record exists
                    donor = BloodDonor.objects.filter(user_id=user.id).first()
                    donor_id = donor.id if donor else None

                    response_data = {
                        "status": "success",
                        "message": "User logged in successfully",
                        "user_id": str(user.id),
                        "donor_id": donor_id,     # Added here
                        "data": request.data
                    }

                    request.session['id'] = user.id
                    return Response(response_data, status=status.HTTP_200_OK)

                else:
                    return Response({
                        "status": "failed",
                        "message": "Invalid credentials",
                        "data": request.data
                    }, status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                return Response({
                    "status": "failed",
                    "message": "User not found",
                    "data": request.data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response({
            "status": "failed",
            "message": "Invalid input",
            "errors": serializer.errors,
            "data": request.data
        }, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class=UserSerializer
    
    def list(self, request, *args,**kwargs):
        user_id= request.query_params.get('user_id')
        
        if user_id:
            try:
                user= self.queryset.get(id=user_id)
                serializer = self.get_serializer(user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"detail":"User not found"},status=status.HTTP_404_NOT_FOUND)
        else:
            return super().list(request,*args,**kwargs)
        
        
class DepartmentListView(APIView):
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response({"departments": serializer.data}, status=status.HTTP_200_OK)
    
    
# class AvailableDoctorsView(APIView):
#     def get(self, request):
#         department_id = request.query_params.get('department_id')
#         date_str = request.query_params.get('date')

#         if not department_id or not date_str:
#             return Response(
#                 {"error": "department_id and date are required query parameters."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Validate and convert date
#         try:
#             date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         # Get weekday name (monday, tuesday, etc.)
#         day_name = date_obj.strftime('%A').lower()

#         try:
#             department = Department.objects.get(id=department_id)
#         except Department.DoesNotExist:
#             return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Filter doctors who belong to department and work on that day
#         doctors = Doctor.objects.filter(
#             specialization=department,
#             working_days__icontains=day_name,
#             is_approved=True
#         )

#         serializer = DoctorSerializer(doctors, many=True)
#         return Response({
#             "department": department.department,
#             "date": date_str,
#             "available_doctors": serializer.data
#         })
        
from datetime import datetime

class AvailableDoctorsView(APIView):
    def get(self, request):
        department_id = request.query_params.get('department_id')
        date_str = request.query_params.get('date')

        if not department_id or not date_str:
            return Response(
                {"error": "department_id and date are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        day_name = date_obj.strftime('%A').lower()

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response(
                {"error": "Department not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        doctors = Doctor.objects.filter(
            specialization=department,
            working_days__icontains=day_name,
            status='approved'
        )

        serializer = DoctorSerializer(doctors, many=True)

        return Response({
            "department": department.department,
            "date": date_str,
            "available_doctors": serializer.data
        })


class ExpectedTokenNumberView(APIView):
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date = request.query_params.get('date')

        if not doctor_id or not date:
            return Response(
                {"error": "doctor_id and date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Doctor not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Count total tokens booked for this doctor on the given date
        time_slot = request.query_params.get('time_slot', 'morning')
        total_tokens = Appointment.objects.filter(doctor=doctor, date=date, time_slot=time_slot).count()
        expected_token = total_tokens + 1  # token numbers start from 1 daily

        return Response({
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "date": date,
            "time_slot": time_slot,
            "expected_token_number": expected_token
        })
        

class AppointmentBookingView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Book an appointment with time slot (morning/evening).
        Morning: 40 slots (1-40), Evening: 40 slots (1-40)
        Total: 80 slots per doctor per day
        """
        user_id = request.data.get('user')
        doctor_id = request.data.get('doctor')
        date = request.data.get('date')
        time_slot = request.data.get('time_slot', 'morning')  # 'morning' or 'evening'
        symptoms = request.data.get('symptoms', '')

        # ✅ Validate time_slot
        if time_slot not in ['morning', 'evening']:
            return Response({'error': 'time_slot must be "morning" or "evening"'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate user
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validate doctor
        if not doctor_id:
            return Response({'error': 'Doctor ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'error': 'Invalid doctor ID'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Check if doctor has RESCHEDULED this day/slot
        is_rescheduled = RescheduleRequest.objects.filter(
            doctor=doctor,
            appointment_date=date,
            status='approved'
        ).filter(
            Q(time_slot=time_slot) | Q(time_slot='all_day')
        ).exists()

        if is_rescheduled:
            return Response(
                {'error': f'Doctor is unavailable on {date} ({time_slot}).'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Check slot availability for the specified time slot
        booked_slots = Appointment.objects.filter(
            doctor=doctor, 
            date=date, 
            time_slot=time_slot
        ).count()
        
        if booked_slots >= 40:
            return Response(
                {'error': f'{time_slot.capitalize()} slots are fully booked (40/40)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Generate next token for this time slot
        last_token = Appointment.objects.filter(
            doctor=doctor, 
            date=date, 
            time_slot=time_slot
        ).aggregate(Max('token_number'))['token_number__max']
        next_token = (last_token or 0) + 1

        # ✅ Create appointment
        appointment = Appointment.objects.create(
            user=user,
            doctor=doctor,
            date=date,
            time_slot=time_slot,
            token_number=next_token,
            symptoms=symptoms,
            payment_status='pending',
            status='upcoming'
        )

        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': 'Appointment booked successfully',
            'appointment': serializer.data,
            'token_number': next_token,
            'time_slot': time_slot
        }, status=status.HTTP_201_CREATED)
        
        
class CardPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Process card payment for an appointment.
        Marks payment_status as completed, but appointment remains 'upcoming'
        until the doctor adds a prescription.
        """
        appointment_id = request.data.get('appointment_id')
        cardholder_name = request.data.get('cardholder_name')
        card_number = request.data.get('card_number')
        expiry_date = request.data.get('expiry_date')
        cvv = request.data.get('cvv')

        # ✅ Validate input
        if not all([appointment_id, cardholder_name, card_number, expiry_date, cvv]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch appointment
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'error': 'Invalid appointment ID.'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if already paid
        if appointment.payment_status == 'completed':
            return Response({
                'message': 'Payment already completed.',
                'token_number': appointment.token_number
            }, status=status.HTTP_200_OK)

        # ✅ Assign token number (if not already assigned)
        if not appointment.token_number:
            last_token = Appointment.objects.filter(
                doctor=appointment.doctor,
                date=appointment.date,
                time_slot=appointment.time_slot
            ).aggregate(Max('token_number'))['token_number__max']
            next_token = (last_token or 0) + 1
            appointment.token_number = next_token
        else:
            next_token = appointment.token_number

        # ✅ Mark payment as completed but status remains 'upcoming'
        appointment.payment_status = 'completed'
        appointment.save()

        # ✅ Create Payment record
        Payment.objects.create(
            appointment=appointment,
            method='card',
            amount=100.00,
            cardholder_name=cardholder_name,
            card_number=card_number[-4:],  # only store last 4 digits
            expiry_date=expiry_date,
            cvv='****'  # mask CVV
        )

        # ✅ Return success
        return Response({
            'message': 'Card payment successful!',
            'appointment_id': appointment.id,
            'doctor': appointment.doctor.name,
            'date': appointment.date,
            'token_number': next_token,
            'amount': 100.00,
            'payment_status': 'completed',
            'status': appointment.status  # still 'upcoming'
        }, status=status.HTTP_200_OK)
        
        
class UPIPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Process UPI payment for an appointment.
        Marks payment_status as completed, keeps appointment upcoming.
        """
        appointment_id = request.data.get('appointment_id')
        upi_id = request.data.get('upi_id')

        # ✅ Validate input
        if not appointment_id or not upi_id:
            return Response({'error': 'Appointment ID and UPI ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Fetch appointment
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'error': 'Invalid appointment ID.'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if already paid
        if appointment.payment_status == 'completed':
            return Response({
                'message': 'Payment already completed.',
                'token_number': appointment.token_number
            }, status=status.HTTP_200_OK)

        # ✅ Assign next token if not already assigned
        if not appointment.token_number:
            last_token = Appointment.objects.filter(
                doctor=appointment.doctor,
                date=appointment.date,
                time_slot=appointment.time_slot
            ).aggregate(Max('token_number'))['token_number__max']
            next_token = (last_token or 0) + 1
            appointment.token_number = next_token
        else:
            next_token = appointment.token_number

        # ✅ Mark payment as completed (status stays upcoming)
        appointment.payment_status = 'completed'
        appointment.save()

        # ✅ Create Payment record
        Payment.objects.create(
            appointment=appointment,
            method='upi',
            amount=100.00,
            upi_id=upi_id
        )

        # ✅ Return success
        return Response({
            'message': 'UPI payment successful!',
            'appointment_id': appointment.id,
            'doctor': appointment.doctor.name,
            'date': appointment.date,
            'token_number': next_token,
            'amount': 100.00,
            'payment_status': 'completed',
            'payment_method': 'upi',
            'status': appointment.status  # still upcoming
        }, status=status.HTTP_200_OK)
        
# class UserUpcomingAppointmentsAPIView(APIView):

#     def get(self, request):
#         # user_id should come from query for GET
#         user_id = request.GET.get("user_id")

#         if not user_id:
#             return Response(
#                 {"success": False, "detail": "user_id is required."},
#                 status=http_status.HTTP_400_BAD_REQUEST
#             )

#         # fetch only upcoming appointments
#         appointments = Appointment.objects.filter(
#             user_id=user_id,
#             status="upcoming"
#         ).order_by("date", "token_number")

#         serializer = AppointmentSerializer(appointments, many=True)

#         return Response(
#             {
#                 "success": True,
#                 "count": len(serializer.data),
#                 "appointments": serializer.data
#             },
#             status=http_status.HTTP_200_OK
#         )

class UpcomingAppointmentsView(APIView):

    def get(self, request, *args, **kwargs):

        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response({"success": False, "error": "user_id is required"}, status=400)

        today = timezone.now().date()

        # Fetch upcoming appointments (future only)
        appointments = Appointment.objects.filter(
            user_id=user_id,
            status="upcoming",
            date__gte=today
        ).order_by("date", "token_number")

        serializer = AppointmentListSerializer(appointments, many=True)

        return Response({
            "success": True,
            "count": len(appointments),
            "appointments": serializer.data
        }, status=200)
        
class UserAppointmentListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {"success": False, "message": "user_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure user exists
        user = get_object_or_404(User, id=user_id)

        # Fetch appointments for the user
        appointments = Appointment.objects.filter(user=user).order_by('-date')

        # Serialize the data
        serializer = AppointmentListSerializer(appointments, many=True)

        return Response({
            "success": True,
            "user": user.username,
            "appointments": serializer.data
        }, status=status.HTTP_200_OK)
        
        
# class AppointmentDetailView(APIView):
#     def get(self, request):
#         appointment_id = request.query_params.get('appointment_id')

#         if not appointment_id:
#             return Response(
#                 {"success": False, "message": "appointment_id parameter is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         appointment = get_object_or_404(Appointment, id=appointment_id)
#         serializer = AppointmentDetailSerializer(appointment)

#         return Response({
#             "success": True,
#             "appointment": serializer.data
#         }, status=status.HTTP_200_OK)
class AppointmentDetailView(APIView):
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')

        if not appointment_id:
            return Response(
                {"success": False, "message": "appointment_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment = get_object_or_404(Appointment, id=appointment_id)

        # ⭐ Check if feedback exists
        has_feedback = Feedback.objects.filter(appointment=appointment).exists()

        serializer = AppointmentDetailSerializer(appointment)

        return Response({
            "success": True,
            "has_feedback": has_feedback,
            "appointment": serializer.data
        }, status=status.HTTP_200_OK)

        
class CancelAppointmentView(APIView):
    def patch(self, request):
        appointment_id = request.data.get('appointment_id')
        reason = request.data.get('reason')

        if not appointment_id:
            return Response(
                {"success": False, "message": "appointment_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reason:
            return Response(
                {"success": False, "message": "Cancellation reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Allow cancellation for upcoming or rescheduled appointments
        if appointment.status not in ['upcoming', 'rescheduled']:
            return Response(
                {"success": False, "message": "Only upcoming or rescheduled appointments can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the appointment
        appointment.status = 'cancelled'
        appointment.cancellation_reason = reason
        appointment.save()

        return Response({
            "success": True,
            "message": f"Appointment #{appointment.id} has been cancelled successfully."
        }, status=status.HTTP_200_OK)        
        
        
class UserPrescriptionsView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        # ✅ Validate input
        if not user_id:
            return Response(
                {"success": False, "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Fetch prescriptions linked to this user's appointments
        prescriptions = Prescription.objects.filter(
            appointment__user_id=user_id
        ).select_related('appointment__doctor').prefetch_related('medicines')

        if not prescriptions.exists():
            return Response({
                "success": True,
                "user_id": user_id,
                "prescriptions": []
            })

        serializer = PrescriptionSerializer(prescriptions, many=True)

        return Response({
            "success": True,
            "user_id": user_id,
            "prescriptions": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class PrescriptionDetailView(APIView):
     def get(self, request):
        # ✅ Get prescription_id from query params
        prescription_id = request.query_params.get('prescription_id')

        if not prescription_id:
            return Response(
                {"error": "prescription_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Get prescription or return 404
        prescription = get_object_or_404(Prescription, id=prescription_id)

        appointment = prescription.appointment
        doctor = appointment.doctor
        user = appointment.user

        # ✅ Medicines for this prescription
        medicines = Medicine.objects.filter(prescription=prescription)
        medicines_data = [
            {
                "id": med.id,
                "name": med.name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "time_of_day": med.time_of_day,
                "food_instruction": med.food_instruction,
                "number_of_days": med.number_of_days,
            }
            for med in medicines
        ]

        # ✅ Structured response
        data = {
            "prescription_id": prescription.id,
            "symptoms": prescription.symptoms,
            "notes": prescription.notes,
            "appointment": {
                "id": appointment.id,
                "date": appointment.date,
                "status": appointment.status,
                "token_number": appointment.token_number,
            },
            "doctor": {
                "id": doctor.id,
                "name": doctor.name,
                "email": doctor.email,
                "specialization": (
                    doctor.specialization.department if doctor.specialization else "General"
                ),
            },
            "patient": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": getattr(user, "phone_number", ""),
            },
            "medicines": medicines_data,
        }

        return Response(data, status=status.HTTP_200_OK)
    
    

class SubmitFeedbackView(APIView):
    """
    POST - Submit feedback for an appointment
    Params:
        appointment_id (int)
        star_rating (int)
        doctor_interaction_rating (float)
        hospital_service_rating (float)
        comments (optional)
    """

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        star_rating = request.data.get('star_rating')
        doctor_interaction = request.data.get('doctor_interaction_rating')
        hospital_service = request.data.get('hospital_service_rating')
        comments = request.data.get('comments', '')

        # ✅ Validate required fields
        if not appointment_id or not star_rating or not doctor_interaction or not hospital_service:
            return Response(
                {"error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Check appointment
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # ✅ Prevent duplicate feedback
        if hasattr(appointment, 'feedback'):
            return Response(
                {"message": "Feedback already submitted for this appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Save feedback
        feedback = Feedback.objects.create(
            appointment=appointment,
            star_rating=int(star_rating),
            doctor_interaction_rating=float(doctor_interaction),
            hospital_service_rating=float(hospital_service),
            comments=comments,
        )

        return Response({
            "success": True,
            "message": "Feedback submitted successfully.",
            "data": {
                "feedback_id": feedback.id,
                "appointment_id": appointment.id,
                "star_rating": feedback.star_rating,
                "doctor_interaction_rating": feedback.doctor_interaction_rating,
                "hospital_service_rating": feedback.hospital_service_rating,
                "comments": feedback.comments,
            }
        }, status=status.HTTP_201_CREATED)
        
        
class FeedbackListView(APIView):
    """
    GET - List all feedback submitted by a specific user (patient)
    Params:
        user_id (required)
    Response:
        List of feedback with doctor & appointment details
    """

    def get(self, request):
        user_id = request.query_params.get('user_id')

        # ✅ Validate param
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Get all feedbacks for appointments of this user
        feedbacks = Feedback.objects.filter(appointment__user_id=user_id).select_related(
            'appointment__doctor'
        ).order_by('-created_at')

        if not feedbacks.exists():
            return Response({"message": "No feedback found for this user."}, status=status.HTTP_200_OK)

        # ✅ Prepare structured response
        feedback_list = []
        for fb in feedbacks:
            appointment = fb.appointment
            doctor = appointment.doctor

            feedback_list.append({
                "feedback_id": fb.id,
                "appointment_id": appointment.id,
                "appointment_date": appointment.date,
                "doctor": {
                    "id": doctor.id,
                    "name": doctor.name,
                    "specialization": (
                        doctor.specialization.department if doctor.specialization else "General"
                    ),
                    "email": doctor.email,
                },
                "star_rating": fb.star_rating,
                "doctor_interaction_rating": fb.doctor_interaction_rating,
                "hospital_service_rating": fb.hospital_service_rating,
                "comments": fb.comments,
                "submitted_on": fb.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return Response({
            "user_id": user_id,
            "feedback_count": len(feedback_list),
            "feedback": feedback_list
        }, status=status.HTTP_200_OK)
        
        
class FeedbackDetailView(APIView):

    def get(self, request):
        feedback_id = request.query_params.get('feedback_id')

        if not feedback_id:
            return Response(
                {"error": "feedback_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        feedback = get_object_or_404(Feedback, id=feedback_id)
        appointment = feedback.appointment
        doctor = appointment.doctor
        user = appointment.user

        # Doctor image path (media/...)
        doctor_image_path = ""
        if doctor.image:
            doctor_image_path = f"media/{doctor.image.name}"

        data = {
            "feedback_id": feedback.id,
            "appointment": {
                "id": appointment.id,
                "date": appointment.date,
                "status": appointment.status,
                "token_number": appointment.token_number,
                "doctor": {
                    "id": doctor.id,
                    "name": doctor.name,
                    "specialization": doctor.specialization.department if doctor.specialization else "General",
                    "email": doctor.email,
                    "image": doctor_image_path,   # ✅ Updated: media/...
                },
                "patient": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": getattr(user, "phone_number", ""),
                },
            },
            "feedback": {
                "star_rating": feedback.star_rating,
                "doctor_interaction_rating": feedback.doctor_interaction_rating,
                "hospital_service_rating": feedback.hospital_service_rating,
                "comments": feedback.comments,
                "submitted_on": feedback.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }

        return Response(data, status=status.HTTP_200_OK)
    
class BookingConfirmationView(APIView):
    """
    GET - Fetch appointment details for booking confirmation screen
    Params:
        appointment_id (required)
    Response:
        Token number, doctor name, department name, date, expected time
    """

    def get(self, request):
        # ✅ Get appointment ID from params
        appointment_id = request.query_params.get('appointment_id')

        if not appointment_id:
            return Response(
                {"error": "appointment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Fetch appointment
        appointment = get_object_or_404(Appointment, id=appointment_id)
        doctor = appointment.doctor

        # ✅ Calculate expected time (same logic used in your mail)
        BUFFER_MINUTES = 15
        token_time_minutes = (appointment.token_number - 1) * 10
        start_time = datetime.strptime("09:00", "%H:%M")  # Assuming OP starts at 9 AM
        expected_time = (
            start_time + timedelta(minutes=BUFFER_MINUTES + token_time_minutes)
        ).strftime("%I:%M %p")

        # ✅ Prepare response data
        data = {
            "appointment_id": appointment.id,
            "token_number": appointment.token_number,
            "doctor_name": doctor.name,
            "department_name": (
                doctor.specialization.department if doctor.specialization else "General"
            ),
            "date": appointment.date.strftime("%Y-%m-%d"),
            "expected_time": expected_time,
        }

        return Response(data, status=status.HTTP_200_OK)


class AcceptRescheduleAPIView(APIView):

    def patch(self, request):
        appt_id = request.data.get("appointment_id")
        user_id = request.data.get("user_id")

        if not appt_id or not user_id:
            return Response(
                {"success": False, "detail": "appointment_id and user_id are required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        appt = get_object_or_404(Appointment, id=appt_id, user_id=user_id)

        if appt.status != "rescheduled" or not appt.rescheduled_date:
            return Response(
                {"success": False, "detail": "No pending reschedule for this appointment."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()
        cutoff = appt.rescheduled_date - timedelta(days=1)  # <-- FIXED

        if today > cutoff:
            appt.status = "cancelled"
            appt.cancellation_reason = "User failed to accept before cutoff."
            appt.save()
            return Response(
                {"success": False, "detail": "Acceptance window closed — appointment cancelled."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        new_date = appt.rescheduled_date
        doctor = appt.doctor

        existing_appts = Appointment.objects.filter(
            doctor=doctor,
            date=new_date
        ).exclude(id=appt.id)

        if existing_appts.exists():
            new_token = existing_appts.count() + 1
        else:
            new_token = 1

        appt.date = new_date
        appt.rescheduled_date = None
        appt.status = "upcoming"
        appt.cancellation_reason = None
        appt.token_number = new_token
        appt.save()

        return Response(
            {
                "success": True,
                "message": "Appointment rescheduled successfully.",
                "appointment_id": appt.id,
                "new_date": appt.date,
                "new_token": new_token,
            },
            status=http_status.HTTP_200_OK,
        )

        
class RejectRescheduleAPIView(APIView):

    def patch(self, request):
        # -----------------------------
        # 1. Read required fields
        # -----------------------------
        appt_id = request.data.get("appointment_id")
        user_id = request.data.get("user_id")

        if not appt_id or not user_id:
            return Response(
                {"success": False, "detail": "appointment_id and user_id are required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------
        # 2. Get appointment for that user
        # -----------------------------
        appt = get_object_or_404(Appointment, id=appt_id, user_id=user_id)

        # -----------------------------
        # 3. Ensure it is rescheduled
        # -----------------------------
        if appt.status != "rescheduled" or not appt.rescheduled_date:
            return Response(
                {"success": False, "detail": "No pending reschedule for this appointment."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------
        # 4. User Rejects → Cancel appointment
        # -----------------------------
        appt.status = "cancelled"
        appt.cancellation_reason = "User rejected the reschedule."
        appt.save()

        return Response(
            {
                "success": True,
                "message": "Appointment cancelled successfully.",
                "appointment_id": appt.id,
            },
            status=http_status.HTTP_200_OK,
        )


# class BloodDonorRegisterView(APIView):

#     def post(self, request, *args, **kwargs):
#         serializer = BloodDonorSerializer(data=request.data)
        
#         if serializer.is_valid():
#             donor = serializer.save()
#             return Response({
#                 "success": True,
#                 "message": "Blood donor registered successfully.",
#                 "data": BloodDonorSerializer(donor).data
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "success": False,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


class BloodDonorRegisterView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = BloodDonorSerializer(data=request.data)

        if serializer.is_valid():

            user_id = serializer.validated_data.get("user_id")

            # Check if donor already registered
            existing_donor = BloodDonor.objects.filter(user_id=user_id).first()
            if existing_donor:
                return Response({
                    "success": False,
                    "message": "This user is already registered as a blood donor.",
                    "donor_id": existing_donor.id,
                    "data": BloodDonorSerializer(existing_donor).data
                }, status=status.HTTP_400_BAD_REQUEST)

            donor = serializer.save()
            return Response({
                "success": True,
                "message": "Blood donor registered successfully.",
                "data": BloodDonorSerializer(donor).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




# class UserNotificationsView(ListAPIView):
#     serializer_class = NotificationSerializer

#     def list(self, request, *args, **kwargs):
#         user_id = request.query_params.get("user_id")

#         # Validate parameter
#         if not user_id:
#             return Response(
#                 {"error": "user_id query parameter is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Validate user exists
#         if not User.objects.filter(id=user_id).exists():
#             return Response(
#                 {"error": "User not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Fetch notifications
#         notifications = Notification.objects.filter(
#             user_id=user_id
#         ).order_by("-created_at")

#         serializer = self.get_serializer(notifications, many=True)
#         return Response(serializer.data, status=200)



class UserNotificationsView(ListAPIView):
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")

        # Validate
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        if not User.objects.filter(id=user_id).exists():
            return Response({"error": "User not found"}, status=404)

        # ---------------------------------------------------
        # Base queryset (ALL notifications)
        # ---------------------------------------------------
        qs = Notification.objects.filter(user_id=user_id).order_by("-created_at")

        # ---------------------------------------------------
        # ⭐ NEW: Apply blood notification filtering for donors
        # ---------------------------------------------------
        try:
            donor = BloodDonor.objects.get(user_id=user_id)

            qs = Notification.objects.filter(
                user_id=user_id
            ).filter(
                Q(type="reschedule") |
                (
                    Q(type="blood") &
                    Q(message__icontains=donor.blood_group) &
                    Q(message__icontains=donor.location.capitalize())
                )
            ).order_by("-created_at")

        except BloodDonor.DoesNotExist:
            pass  # user is not a donor → return all notifications

        # ---------------------------------------------------
        # ⭐ No limit applied → return ALL
        # ---------------------------------------------------

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    
class AcceptBloodRequestView(APIView):

    def post(self, request, *args, **kwargs):
        donor_id = request.data.get("donor_id")
        request_id = request.data.get("request_id")

        # ----------- Validate donor -----------
        try:
            donor = BloodDonor.objects.get(id=donor_id)
        except BloodDonor.DoesNotExist:
            return Response(
                {"error": "Invalid donor_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ----------- Validate blood request -----------
        try:
            blood_req = BloodRequest.objects.get(id=request_id, status="approved")
        except BloodRequest.DoesNotExist:
            return Response(
                {"error": "Blood request not found or not approved yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        donation_type = blood_req.donation_type

        # **********************************************************
        #   ⭐ CHECK MINIMUM DONATION INTERVAL
        # **********************************************************
        last_date = donor.last_donation_date

        if last_date:
            today = timezone.now().date()

            # Determine required interval
            if donation_type == "Whole Blood":
                required_gap = timedelta(days=56)
            elif donation_type == "Red Cells":
                required_gap = timedelta(days=112)
            elif donation_type == "Plasma":
                required_gap = timedelta(days=14)
            elif donation_type == "Platelets":
                required_gap = timedelta(days=7)
            else:
                required_gap = timedelta(days=56)  # default safety rule

            next_eligible_date = last_date + required_gap

            # Not eligible yet
            if today < next_eligible_date:
                return Response(
                    {
                        "error": "Donor not eligible for donation yet",
                        "last_donation_date": str(last_date),
                        "next_eligible_date": str(next_eligible_date),
                        "required_gap_days": required_gap.days
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # **********************************************************
        #   Prevent duplicate acceptance
        # **********************************************************
        if DonorAcceptance.objects.filter(donor=donor, request=blood_req).exists():
            return Response(
                {"message": "You have already accepted this blood request"},
                status=status.HTTP_200_OK
            )

        # ----------- Create acceptance record -----------
        DonorAcceptance.objects.create(
            donor=donor,
            request=blood_req
        )

        return Response(
            {"message": "Donation accepted successfully!"},
            status=status.HTTP_201_CREATED
        )
        

class AddDonationRecordView(APIView):

    def post(self, request, *args, **kwargs):
        donor_id = request.data.get("donor_id")
        donation_date = request.data.get("date")
        location = request.data.get("location")
        donation_type = request.data.get("donation_type")
        units = request.data.get("units")

        # -------- Validate donor --------
        try:
            donor = BloodDonor.objects.get(id=donor_id)
        except BloodDonor.DoesNotExist:
            return Response(
                {"error": "Invalid donor_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -------- Validate required fields --------
        if not donation_date or not location or not donation_type or not units:
            return Response(
                {"error": "All fields (date, location, donation_type, units) are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------- Create Donation Record --------
        record = DonationRecord.objects.create(
            donor=donor,
            donation_date=donation_date,
            location=location,
            donation_type=donation_type,
            units=units
        )

        # -------- Update Donor Last Donation Date --------
        donor.last_donation_date = donation_date
        donor.save()

        return Response(
            {
                "message": "Donation record added successfully!",
                "record_id": record.id
            },
            status=status.HTTP_201_CREATED
        )
        
        
# class BloodRequestsForDonorView(APIView):

#     def get(self, request, *args, **kwargs):
#         donor_id = request.query_params.get("donor_id")

#         # ---------- Validate donor ----------
#         try:
#             donor = BloodDonor.objects.get(id=donor_id)
#         except BloodDonor.DoesNotExist:
#             return Response(
#                 {"error": "Invalid donor_id"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         today = timezone.now().date()

#         # ---------- Filter blood requests ----------
#         requests = BloodRequest.objects.filter(
#             blood_group=donor.blood_group,
#             status="approved"  # only approved ones are meaningful for donor
#         ).filter(
#             # Do not show past donation dates
#             Q(donation_date__gte=today) | Q(donation_date__isnull=True)
#         ).order_by("-created_at")

#         # ---------- Format response ----------
#         data = [
#             {
#                 "id": req.id,
#                 "doctor": req.doctor.name,
#                 "blood_group": req.blood_group,
#                 "units_required": req.units_required,
#                 "donation_type": req.donation_type,
#                 "donation_date": req.donation_date,
#                 "location": req.location,
#                 "reason": req.reason,
#                 "created_at": req.created_at,
#             }
#             for req in requests
#         ]

#         return Response(data, status=200)

class BloodRequestsForDonorView(APIView):

    def get(self, request, *args, **kwargs):
        donor_id = request.query_params.get("donor_id")

        # ---------- Validate donor ----------
        try:
            donor = BloodDonor.objects.get(id=donor_id)
        except BloodDonor.DoesNotExist:
            return Response(
                {"error": "Invalid donor_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.now().date()

        # ---------- Find requests already accepted by this donor ----------
        accepted_request_ids = DonorAcceptance.objects.filter(
            donor_id=donor_id
        ).values_list("request_id", flat=True)

        # ---------- Filter blood requests ----------
        requests = (
            BloodRequest.objects.filter(
                blood_group=donor.blood_group,
                status="approved"
            )
            .filter(
                Q(donation_date__gte=today) | Q(donation_date__isnull=True)
            )
            .exclude(id__in=accepted_request_ids)   # hide already accepted
            .order_by("-created_at")
        )

        # ---------- Format response ----------
        data = [
            {
                "id": req.id,
                "doctor": req.doctor.name,
                "blood_group": req.blood_group,
                "units_required": req.units_required,
                "donation_type": req.donation_type,
                "donation_date": req.donation_date,
                "location": req.location,
                "reason": req.reason,
                "created_at": req.created_at,
            }
            for req in requests
        ]

        return Response(data, status=200)

    
# class CommonBloodRequestListView(APIView):

#     def get(self, request, *args, **kwargs):
#         today = timezone.now().date()

#         # Fetch all approved & non-expired blood requests
#         requests = BloodRequest.objects.filter(
#             status="approved"
#         ).filter(
#             Q(donation_date__gte=today) | Q(donation_date__isnull=True)
#         ).order_by("-created_at")

#         data = [
#             {
#                 "id": req.id,
#                 "doctor": req.doctor.name,
#                 "blood_group": req.blood_group,
#                 "units_required": req.units_required,
#                 "donation_type": req.donation_type,
#                 "donation_date": req.donation_date,
#                 "location": req.location,
#                 "reason": req.reason,
#                 "created_at": req.created_at,
#             }
#             for req in requests
#         ]

#         return Response(data, status=200)

class CommonBloodRequestListView(APIView):

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Show only today's and future requests
        requests = BloodRequest.objects.filter(
            status="approved",
        ).filter(
            Q(donation_date__gte=today) | Q(donation_date__isnull=True)
        ).order_by("-created_at")

        data = [
            {
                "id": req.id,
                "doctor": req.doctor.name,
                "blood_group": req.blood_group,
                "units_required": req.units_required,
                "donation_type": req.donation_type,
                "donation_date": req.donation_date,
                "location": req.location,
                "reason": req.reason,
                "created_at": req.created_at,
            }
            for req in requests
        ]

        return Response(data, status=200)

    
    
class DonorDonationHistoryView(APIView):

    def get(self, request, *args, **kwargs):
        donor_id = request.query_params.get("donor_id")

        # Validate donor
        try:
            donor = BloodDonor.objects.get(id=donor_id)
        except BloodDonor.DoesNotExist:
            return Response(
                {"error": "Invalid donor_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch all donation records
        records = DonationRecord.objects.filter(
            donor=donor
        ).order_by("-donation_date")

        # Format response
        data = [
            {
                "record_id": record.id,
                "donation_date": record.donation_date,
                "location": record.location,
                "donation_type": record.donation_type,
                "units": record.units,
                "created_at": record.created_at,
            }
            for record in records
        ]

        return Response(data, status=200)
    
from django.utils.timezone import now

class DoctorCurrentTokenView(APIView):
    def get(self, request):

        doctor_id = request.query_params.get("doctor_id")

        if not doctor_id:
            return Response({
                "status": "error",
                "message": "doctor_id is required"
            }, status=400)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"status": "error", "message": "Doctor not found"}, status=404)

        today = now().date()

        # Valid today's appointments
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today,
            payment_status="completed"
        ).exclude(
            status__in=["cancelled", "rescheduled", "completed"]
        ).order_by("token_number")

        if not appointments.exists():
            return Response({
                "status": "success",
                "current_token": None,
                "next_token": None,
                "total_tokens": 0
            })

        # ----- FIX: treat 'upcoming' as waiting -----
        current_app = (
            appointments.filter(status="in_progress").first()
            or appointments.filter(status__in=["waiting", "upcoming"]).first()
        )

        # Next token
        next_app = None
        if current_app:
            next_app = appointments.filter(
                token_number__gt=current_app.token_number,
                status__in=["waiting", "upcoming"]
            ).first()

        return Response({
            "status": "success",
            "doctor": doctor.name,
            "current_token": {
                "token_number": current_app.token_number if current_app else None,
                "patient_name": current_app.user.username if current_app else None,
                "appointment_id": current_app.id if current_app else None,
            },
            "next_token": {
                "token_number": next_app.token_number if next_app else None,
                "patient_name": next_app.user.username if next_app else None,
                "appointment_id": next_app.id if next_app else None,
            },
            "total_tokens": appointments.count()
        })


class AppointmentPrescriptionStatusView(APIView):
    def get(self, request):
        appointment_id = request.query_params.get("appointment_id")

        if not appointment_id:
            return Response(
                {"success": False, "message": "appointment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get appointment
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid appointment ID"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ❌ If prescription does NOT exist → return error
        if not hasattr(appointment, "prescription"):
            return Response({
                "success": False,
                "message": "Prescription not available. Appointment not completed.",
                "appointment": {
                    "id": appointment.id,
                    "doctor_name": appointment.doctor.name,
                    "user_name": appointment.user.username,
                    "date": appointment.date,
                    "status": appointment.status
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ If prescription exists → return completed info
        prescription = appointment.prescription
        medicines = prescription.medicines.all()

        med_list = [
            {
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "time_of_day": m.time_of_day,
                "food_instruction": m.food_instruction,
                "number_of_days": m.number_of_days
            }
            for m in medicines
        ]

        return Response({
            "success": True,
            "completed": True,
            "message": "Appointment is completed. Prescription available.",
            "appointment": {
                "id": appointment.id,
                "doctor_name": appointment.doctor.name,
                "user_name": appointment.user.username,
                "date": appointment.date,
                "status": appointment.status,
            },
            "prescription": {
                "symptoms": prescription.symptoms,
                "notes": prescription.notes,
                "created_at": prescription.created_at,
                "medicines": med_list
            }
        }, status=status.HTTP_200_OK)



class SubmitComplaintAPIView(APIView):

    def post(self, request):
        user_id = request.data.get("user")
        category = request.data.get("category")
        description = request.data.get("description")

        # images are OPTIONAL
        images = request.FILES.getlist("images", [])

        if not user_id or not category or not description:
            return Response(
                {"error": "user, category, and description are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid user"},
                status=status.HTTP_404_NOT_FOUND
            )

        complaint = Complaint.objects.create(
            user=user,
            category=category,
            description=description
        )

        # Save images only if provided
        for img in images:
            if img:
                ComplaintImage.objects.create(
                    complaint=complaint,
                    image=img
                )

        serializer = ComplaintSerializer(complaint)
        return Response(
            {
                "success": True,
                "message": "Complaint submitted successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class NextDonationDateAPIView(APIView):
    """
    GET - Get next eligible donation date for a donor
    Params:
        donor_id (required)
    """

    def get(self, request):
        donor_id = request.query_params.get("donor_id")

        if not donor_id:
            return Response(
                {"error": "donor_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        donor = get_object_or_404(BloodDonor, id=donor_id)

        # Total donations count
        total_donations = DonationRecord.objects.filter(donor=donor).count()

        last_donation = (
            DonationRecord.objects
            .filter(donor=donor)
            .order_by("-donation_date")
            .first()
        )

        # No previous donations
        if not last_donation:
            return Response({
                "donor": donor.user.username,
                "blood_group": donor.blood_group,
                "total_donations": total_donations,
                "message": "No previous donation found. You are eligible to donate now.",
                "eligible": True,
                "next_donation_date": timezone.now().date()
            }, status=status.HTTP_200_OK)

        donation_type = last_donation.donation_type
        last_date = last_donation.donation_date

        # Donation intervals (days)
        interval_map = {
            "Whole Blood": 56,
            "Red Cells": 112,
            "Plasma": 28,
            "Platelets": 7,
        }

        gap_days = interval_map.get(donation_type, 56)
        next_donation_date = last_date + timedelta(days=gap_days)

        today = timezone.now().date()
        eligible = today >= next_donation_date

        return Response({
            "donor": donor.user.username,
            "blood_group": donor.blood_group, 
            "total_donations": total_donations,
            "last_donation_date": last_date,
            "last_donation_type": donation_type,
            "next_donation_date": next_donation_date,
            "eligible": eligible
        }, status=status.HTTP_200_OK)


class CheckAvailableSlotsAPIView(APIView):
    """
    GET - Check available slots for a doctor on a specific date
    Params:
        doctor_id (required)
        date (required) - Format: YYYY-MM-DD
    
    Response:
        morning_slots: {available: X, total: 40}
        evening_slots: {available: X, total: 40}
        total_available: X out of 80
    """
    
    def get(self, request):
        doctor_id = request.query_params.get("doctor_id")
        date = request.query_params.get("date")
        
        if not doctor_id or not date:
            return Response(
                {"error": "doctor_id and date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Invalid doctor ID"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Count booked slots for each time slot
        morning_booked = Appointment.objects.filter(
            doctor=doctor,
            date=date_obj,
            time_slot='morning'
        ).count()
        
        evening_booked = Appointment.objects.filter(
            doctor=doctor,
            date=date_obj,
            time_slot='evening'
        ).count()
        
        morning_available = 40 - morning_booked
        evening_available = 40 - evening_booked
        total_available = morning_available + evening_available
        
        return Response({
            "doctor": doctor.name,
            "date": date_obj,
            "morning_slots": {
                "available": morning_available,
                "booked": morning_booked,
                "total": 40
            },
            "evening_slots": {
                "available": evening_available,
                "booked": evening_booked,
                "total": 40
            },
            "total_available": total_available,
            "total_slots": 80,
            "fully_booked": total_available == 0
        }, status=status.HTTP_200_OK)


# ========================
# 🔄 RESCHEDULE API - DOCTOR REQUESTS
# ========================
class DoctorRescheduleRequestAPIView(APIView):
    """
    POST - Doctor requests to reschedule appointments
    Params:
        doctor_id (required)
        appointment_date (required) - Date of appointments to reschedule
        time_slot (required) - 'morning', 'evening', or 'all_day'
        token_start (required) - First token number
        token_end (required) - Last token number
        reason (optional) - Reason for reschedule
    """
    
    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        appointment_date = request.data.get('appointment_date')
        time_slot = request.data.get('time_slot', 'all_day')  # morning, evening, all_day
        
        # Default tokens to 0 (no longer used)
        token_start = request.data.get('token_start', 0)
        token_end = request.data.get('token_end', 0)
        
        reason = request.data.get('reason', '')
        
        # Validate required fields
        if not all([doctor_id, appointment_date]):
            return Response(
                {"error": "doctor_id and appointment_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate time_slot
        if time_slot not in ['morning', 'evening', 'all_day']:
            return Response(
                {"error": "time_slot must be 'morning', 'evening', or 'all_day'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "Invalid doctor ID"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate actual token range from appointments
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date=appointment_date,
            status='upcoming'
        )
        
        if time_slot != 'all_day':
            appointments = appointments.filter(time_slot=time_slot)
            
        token_range = appointments.aggregate(min_token=Min('token_number'), max_token=Max('token_number'))
        
        # Use calculated range or 0-0 if no appointments found
        token_start = token_range['min_token'] or 0
        token_end = token_range['max_token'] or 0
        
        reschedule_req = RescheduleRequest.objects.create(
            doctor=doctor,
            appointment_date=appointment_date,
            token_start=token_start,
            token_end=token_end,
            reason=reason,
            time_slot=time_slot  # Store time slot info
        )
        
        return Response({
            "success": True,
            "message": "Reschedule request submitted successfully",
            "request_id": reschedule_req.id,
            "doctor": doctor.name,
            "appointment_date": appointment_date,
            "time_slot": time_slot,
            "token_range": f"{token_start}-{token_end}",
            "status": "pending"
        }, status=status.HTTP_201_CREATED)


# ========================
# 🔄 RESCHEDULE API - ADMIN APPROVES/REJECTS
# ========================
class AdminReviewRescheduleAPIView(APIView):
    """
    PATCH - Admin approves or rejects reschedule request
    Params:
        request_id (required)
        action (required) - 'approve' or 'reject'
        admin_note (optional)
    
    When approved:
    - Calculates new date as 5 days after appointment_date
    - Updates appointments with status='rescheduled'
    - Sends notifications to affected users
    """
    
    def patch(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')
        admin_note = request.data.get('admin_note', '')
        
        if not request_id or not action:
            return Response(
                {"error": "request_id and action are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ['approve', 'reject']:
            return Response(
                {"error": "action must be 'approve' or 'reject'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reschedule_req = RescheduleRequest.objects.get(id=request_id)
        except RescheduleRequest.DoesNotExist:
            return Response(
                {"error": "Reschedule request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if reschedule_req.status != 'pending':
            return Response(
                {"error": f"Request is already {reschedule_req.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # REJECT
        if action == 'reject':
            reschedule_req.status = 'rejected'
            reschedule_req.admin_note = admin_note
            reschedule_req.processed_at = timezone.now()
            reschedule_req.save()
            
            return Response({
                "success": True,
                "message": "Reschedule request rejected",
                "request_id": reschedule_req.id,
                "status": "rejected"
            }, status=status.HTTP_200_OK)
        
        # APPROVE - Calculate 5 days after appointment_date
        old_date = reschedule_req.appointment_date
        proposed_reschedule_date = old_date + timedelta(days=5)
        
        doctor = reschedule_req.doctor
        time_slot = getattr(reschedule_req, 'time_slot', 'all_day')
        
        # Get matching appointments
        query = Appointment.objects.filter(
            doctor=doctor,
            date=old_date,
            token_number__gte=reschedule_req.token_start,
            token_number__lte=reschedule_req.token_end,
            status='upcoming'
        )
        
        # Filter by time_slot if specified
        if time_slot == 'morning':
            query = query.filter(time_slot='morning')
        elif time_slot == 'evening':
            query = query.filter(time_slot='evening')
        # else: all_day → don't filter by time_slot
        
        affected_count = query.count()
        
        # Update appointments and send notifications
        for appt in query:
            appt.status = 'rescheduled'
            appt.rescheduled_date = proposed_reschedule_date
            appt.save()
            
            # Send notification to user
            Notification.objects.create(
                user=appt.user,
                title="Appointment Rescheduled",
                message=(
                    f"Your appointment with Dr. {doctor.name} originally on {old_date} "
                    f"(Token #{appt.token_number}, {time_slot} slot) has been rescheduled to {proposed_reschedule_date}.\n"
                    f"Reason: {reschedule_req.reason or 'Not provided'}\n\n"
                    f"Please accept or reject the new date."
                ),
                type="reschedule"
            )
        
        # Update reschedule request
        reschedule_req.status = 'approved'
        reschedule_req.admin_note = admin_note
        reschedule_req.rescheduled_date = proposed_reschedule_date
        reschedule_req.processed_at = timezone.now()
        reschedule_req.save()
        
        return Response({
            "success": True,
            "message": f"Reschedule request approved. {affected_count} appointments rescheduled.",
            "request_id": reschedule_req.id,
            "original_date": old_date,
            "new_date": proposed_reschedule_date,
            "affected_appointments": affected_count,
            "time_slot": time_slot,
            "status": "approved"
        }, status=status.HTTP_200_OK)


# ========================
# 🔄 RESCHEDULE API - USER ACCEPTS (EXISTING - UPDATED)
# ========================
class UserAcceptRescheduleAPIView(APIView):
    """
    PATCH - User accepts rescheduled appointment
    Params:
        appointment_id (required)
        user_id (required)
    
    Updates appointment date and generates new token for new date
    """
    
    def patch(self, request):
        appointment_id = request.data.get('appointment_id')
        user_id = request.data.get('user_id')
        
        if not appointment_id or not user_id:
            return Response(
                {"error": "appointment_id and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appt = Appointment.objects.get(id=appointment_id, user_id=user_id)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if appt.status != 'rescheduled' or not appt.rescheduled_date:
            return Response(
                {"error": "No pending reschedule for this appointment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check acceptance window (must accept by 1 day before rescheduled_date)
        today = timezone.localdate()
        cutoff = appt.rescheduled_date - timedelta(days=1)
        
        if today > cutoff:
            appt.status = 'cancelled'
            appt.cancellation_reason = 'User failed to accept before cutoff'
            appt.save()
            return Response(
                {"error": "Acceptance window closed. Appointment cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accept the reschedule - move to new date
        new_date = appt.rescheduled_date
        doctor = appt.doctor
        time_slot = appt.time_slot
        
        # Generate new token for new date (filtered by time_slot)
        last_token = Appointment.objects.filter(
            doctor=doctor,
            date=new_date,
            time_slot=time_slot
        ).aggregate(Max('token_number'))['token_number__max']
        new_token = (last_token or 0) + 1
        
        # Update appointment
        appt.date = new_date
        appt.token_number = new_token
        appt.rescheduled_date = None
        appt.status = 'upcoming'
        appt.save()
        
        return Response({
            "success": True,
            "message": "Appointment rescheduled successfully",
            "appointment_id": appt.id,
            "new_date": new_date,
            "new_token": new_token,
            "time_slot": time_slot,
            "status": "upcoming"
        }, status=status.HTTP_200_OK)


# ========================
# 🔄 RESCHEDULE API - USER REJECTS (EXISTING - UPDATED)
# ========================
class UserRejectRescheduleAPIView(APIView):
    """
    PATCH - User rejects rescheduled appointment
    Params:
        appointment_id (required)
        user_id (required)
    
    Cancels the appointment when user rejects reschedule
    """
    
    def patch(self, request):
        appointment_id = request.data.get('appointment_id')
        user_id = request.data.get('user_id')
        
        if not appointment_id or not user_id:
            return Response(
                {"error": "appointment_id and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appt = Appointment.objects.get(id=appointment_id, user_id=user_id)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if appt.status != 'rescheduled' or not appt.rescheduled_date:
            return Response(
                {"error": "No pending reschedule for this appointment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reject → Cancel appointment
        appt.status = 'cancelled'
        appt.cancellation_reason = 'User rejected the reschedule'
        appt.rescheduled_date = None
        appt.save()
        
        return Response({
            "success": True,
            "message": "Appointment cancelled due to rejection",
            "appointment_id": appt.id,
            "status": "cancelled"
        }, status=status.HTTP_200_OK)

# ========================
# 🩸 BLOOD DONATION ADMIN APIs
# ========================
class BloodDonationAdminLoginAPIView(APIView):
    """
    POST - Blood Donation Admin Login
    Params:
        email (required)
        password (required)
    
    Returns: admin_id, username, hospital_name
    """
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = BloodDonationAdmin.objects.get(email=email, password=password, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            "success": True,
            "message": "Blood Donation Admin login successful",
            "admin_id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "hospital_name": admin.hospital_name,
            "location": admin.location
        }, status=status.HTTP_200_OK)


class BloodDonationAdminViewRequestsAPIView(APIView):
    """
    GET - Blood Donation Admin views all blood requests
    Params:
        admin_id (required)
        status (optional) - pending, approved, rejected
    """
    
    def get(self, request):
        admin_id = request.query_params.get('admin_id')
        filter_status = request.query_params.get('status', '')
        
        if not admin_id:
            return Response(
                {"error": "admin_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin exists
        try:
            admin = BloodDonationAdmin.objects.get(id=admin_id, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid admin"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get blood requests
        requests = BloodRequest.objects.all().order_by('-created_at')
        
        if filter_status:
            requests = requests.filter(status=filter_status)
        
        # Format response
        data = [
            {
                "id": req.id,
                "doctor": req.doctor.name,
                "blood_group": req.blood_group,
                "units_required": req.units_required,
                "donation_type": req.donation_type,
                "donation_date": req.donation_date,
                "location": req.location,
                "reason": req.reason,
                "status": req.status,
                "created_at": req.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for req in requests
        ]
        
        return Response({
            "success": True,
            "admin": admin.username,
            "total_requests": len(data),
            "requests": data
        }, status=status.HTTP_200_OK)


class BloodDonationAdminApproveRequestAPIView(APIView):
    """
    POST - Blood Donation Admin approves blood request
    Params:
        admin_id (required)
        request_id (required)
    
    Sends notifications to matching donors
    """
    
    def post(self, request):
        admin_id = request.data.get('admin_id')
        request_id = request.data.get('request_id')
        
        if not admin_id or not request_id:
            return Response(
                {"error": "admin_id and request_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin
        try:
            admin = BloodDonationAdmin.objects.get(id=admin_id, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid admin"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get blood request
        try:
            blood_req = BloodRequest.objects.get(id=request_id)
        except BloodRequest.DoesNotExist:
            return Response(
                {"error": "Blood request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Approve request
        blood_req.status = 'approved'
        blood_req.save()
        
        # Find matching donors
        donors = BloodDonor.objects.filter(
            blood_group=blood_req.blood_group,
            location=blood_req.location
        )
        
        # Format donation date
        donation_date_text = blood_req.donation_date.strftime("%d-%m-%Y") if blood_req.donation_date else "As soon as possible"
        
        # Send notifications to donors
        for donor in donors:
            Notification.objects.create(
                user=donor.user,
                title="Urgent Blood Donation Needed",
                message=(
                    f"Dear Donor, your blood type {blood_req.blood_group} is urgently needed at {blood_req.location}.\n"
                    f"➡ Donation Type: {blood_req.donation_type}\n"
                    f"➡ Units Required: {blood_req.units_required}\n"
                    f"➡ Preferred Donation Date: {donation_date_text}\n"
                    f"➡ Reason: {blood_req.reason}\n\n"
                    f"Please help if you are available."
                ),
                type="blood"
            )
        
        return Response({
            "success": True,
            "message": "Blood request approved and donors notified",
            "request_id": blood_req.id,
            "donors_notified": donors.count(),
            "status": "approved"
        }, status=status.HTTP_200_OK)


class BloodDonationAdminRejectRequestAPIView(APIView):
    """
    POST - Blood Donation Admin rejects blood request
    Params:
        admin_id (required)
        request_id (required)
        reason (optional)
    """
    
    def post(self, request):
        admin_id = request.data.get('admin_id')
        request_id = request.data.get('request_id')
        reason = request.data.get('reason', '')
        
        if not admin_id or not request_id:
            return Response(
                {"error": "admin_id and request_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin
        try:
            admin = BloodDonationAdmin.objects.get(id=admin_id, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid admin"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get blood request
        try:
            blood_req = BloodRequest.objects.get(id=request_id)
        except BloodRequest.DoesNotExist:
            return Response(
                {"error": "Blood request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Reject request
        blood_req.status = 'rejected'
        blood_req.save()
        
        return Response({
            "success": True,
            "message": "Blood request rejected",
            "request_id": blood_req.id,
            "reason": reason,
            "status": "rejected"
        }, status=status.HTTP_200_OK)


class BloodDonationAdminViewAcceptedDonorsAPIView(APIView):
    """
    GET - Blood Donation Admin views donors who accepted a blood request
    Params:
        admin_id (required)
        request_id (required)
    """
    
    def get(self, request):
        admin_id = request.query_params.get('admin_id')
        request_id = request.query_params.get('request_id')
        
        if not admin_id or not request_id:
            return Response(
                {"error": "admin_id and request_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin
        try:
            admin = BloodDonationAdmin.objects.get(id=admin_id, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid admin"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get blood request
        try:
            blood_req = BloodRequest.objects.get(id=request_id)
        except BloodRequest.DoesNotExist:
            return Response(
                {"error": "Blood request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get accepted donors
        acceptances = DonorAcceptance.objects.filter(request=blood_req).select_related('donor__user')
        
        data = [
            {
                "acceptance_id": acc.id,
                "donor_id": acc.donor.id,
                "donor_name": acc.donor.user.username,
                "blood_group": acc.donor.blood_group,
                "location": acc.donor.location,
                "status": acc.status,
                "accepted_at": acc.accepted_at.strftime("%Y-%m-%d %H:%M:%S") if acc.accepted_at else None
            }
            for acc in acceptances
        ]
        
        return Response({
            "success": True,
            "request_id": blood_req.id,
            "total_accepted": len(data),
            "donors": data
        }, status=status.HTTP_200_OK)


class BloodDonationAdminCompleteDonationAPIView(APIView):
    """
    POST - Blood Donation Admin marks donation as completed
    Params:
        admin_id (required)
        acceptance_id (required)
    
    Creates DonationRecord and updates donor's last_donation_date
    """
    
    def post(self, request):
        admin_id = request.data.get('admin_id')
        acceptance_id = request.data.get('acceptance_id')
        
        if not admin_id or not acceptance_id:
            return Response(
                {"error": "admin_id and acceptance_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify admin
        try:
            admin = BloodDonationAdmin.objects.get(id=admin_id, is_active=True)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Invalid admin"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get acceptance record
        try:
            acceptance = DonorAcceptance.objects.get(id=acceptance_id)
        except DonorAcceptance.DoesNotExist:
            return Response(
                {"error": "Acceptance record not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark as completed
        acceptance.status = 'completed'
        acceptance.save()
        
        donor = acceptance.donor
        blood_req = acceptance.request
        
        # Create donation record
        DonationRecord.objects.create(
            donor=donor,
            donation_date=blood_req.donation_date or timezone.now().date(),
            location=blood_req.location,
            donation_type=blood_req.donation_type,
            units=blood_req.units_required
        )
        
        # Update donor's last donation date
        donor.last_donation_date = blood_req.donation_date or timezone.now().date()
        donor.save()
        
        return Response({
            "success": True,
            "message": "Donation marked as completed",
            "donor": donor.user.username,
            "donation_date": blood_req.donation_date or timezone.now().date(),
            "units": blood_req.units_required
        }, status=status.HTTP_200_OK)

# ========================
# 🩸 ADMIN CREATE BLOOD DONATION ADMIN
# ========================
class AdminCreateBloodDonationAdminAPIView(APIView):
    """
    POST - Admin creates a new Blood Donation Admin
    Params:
        admin_id (required) - ID of regular admin
        admin_email (required) - Email of regular admin (for verification)
        username (required) - Username for new blood donation admin
        email (required) - Email for new blood donation admin
        password (required) - Password for new blood donation admin
        phone_number (required) - Phone number
        hospital_name (required) - Hospital/Blood Bank name
        location (required) - Location (Thrissur, Ernakulam, Palakkad)
    """
    
    def post(self, request):
        admin_id = request.data.get('admin_id')
        admin_email = request.data.get('admin_email')
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')
        hospital_name = request.data.get('hospital_name')
        location = request.data.get('location')
        
        if not all([admin_id, admin_email, username, email, password, phone_number, hospital_name, location]):
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = Admin.objects.get(id=admin_id, email=admin_email)
        except Admin.DoesNotExist:
            return Response(
                {"error": "Invalid admin credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if BloodDonationAdmin.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if BloodDonationAdmin.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_locations = ['Thrissur', 'Ernakulam', 'Palakkad']
        if location not in valid_locations:
            return Response(
                {"error": f"Location must be one of: {', '.join(valid_locations)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blood_admin = BloodDonationAdmin.objects.create(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            hospital_name=hospital_name,
            location=location,
            is_active=True
        )
        
        return Response({
            "success": True,
            "message": "Blood Donation Admin created successfully",
            "blood_admin": {
                "id": blood_admin.id,
                "username": blood_admin.username,
                "email": blood_admin.email,
                "hospital_name": blood_admin.hospital_name,
                "location": blood_admin.location,
                "is_active": blood_admin.is_active
            }
        }, status=status.HTTP_201_CREATED)


class AdminManageBloodDonationAdminsAPIView(APIView):
    """
    GET - Admin views all blood donation admins
    Params:
        admin_id (required)
        admin_email (required)
    """
    
    def get(self, request):
        admin_id = request.query_params.get('admin_id')
        admin_email = request.query_params.get('admin_email')
        
        if not admin_id or not admin_email:
            return Response(
                {"error": "admin_id and admin_email are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = Admin.objects.get(id=admin_id, email=admin_email)
        except Admin.DoesNotExist:
            return Response(
                {"error": "Invalid admin credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        blood_admins = BloodDonationAdmin.objects.all().order_by('-created_at')
        
        data = [
            {
                "id": admin.id,
                "username": admin.username,
                "email": admin.email,
                "hospital_name": admin.hospital_name,
                "location": admin.location,
                "phone_number": admin.phone_number,
                "is_active": admin.is_active
            }
            for admin in blood_admins
        ]
        
        return Response({
            "success": True,
            "total_blood_admins": len(data),
            "blood_admins": data
        }, status=status.HTTP_200_OK)


class AdminDeactivateBloodDonationAdminAPIView(APIView):
    """
    POST - Admin deactivates a blood donation admin account
    Params:
        admin_id (required)
        admin_email (required)
        blood_admin_id (required)
    """
    
    def post(self, request):
        admin_id = request.data.get('admin_id')
        admin_email = request.data.get('admin_email')
        blood_admin_id = request.data.get('blood_admin_id')
        
        if not all([admin_id, admin_email, blood_admin_id]):
            return Response(
                {"error": "admin_id, admin_email, and blood_admin_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            admin = Admin.objects.get(id=admin_id, email=admin_email)
        except Admin.DoesNotExist:
            return Response(
                {"error": "Invalid admin credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            blood_admin = BloodDonationAdmin.objects.get(id=blood_admin_id)
        except BloodDonationAdmin.DoesNotExist:
            return Response(
                {"error": "Blood Donation Admin not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        blood_admin.is_active = False
        blood_admin.save()
        
        return Response({
            "success": True,
            "message": f"Blood Donation Admin '{blood_admin.username}' deactivated",
            "blood_admin_id": blood_admin.id
        }, status=status.HTTP_200_OK)


class UserRescheduleActionView(APIView):
    """
    User accepts or rejects a rescheduled appointment.
    POST:
        appointment_id: int
        action: 'accept' or 'reject'
    """
    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        action = request.data.get('action')

        if not appointment_id or action not in ['accept', 'reject']:
            return Response(
                {"error": "Invalid request. Need appointment_id and action (accept/reject)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        if appt.status != 'rescheduled':
            return Response({"error": "Appointment is not in rescheduled state. Current status: " + appt.status}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'reject':
            appt.status = 'cancelled'
            appt.cancellation_reason = 'User rejected rescheduled date'
            appt.save()
            return Response({"message": "Appointment cancelled."}, status=status.HTTP_200_OK)

        if action == 'accept':
            if not appt.rescheduled_date:
                return Response({"error": "No rescheduled date found"}, status=status.HTTP_400_BAD_REQUEST)

            # Update date and generate new token
            new_date = appt.rescheduled_date
            
            appt.date = new_date
            appt.status = 'upcoming'
            appt.rescheduled_date = None
            
            # Generate new token logic
            last_token = Appointment.objects.filter(
                doctor=appt.doctor, 
                date=new_date, 
                time_slot=appt.time_slot
            ).aggregate(Max('token_number'))['token_number__max']
            
            appt.token_number = (last_token or 0) + 1
            appt.save()
            
            return Response({
                "message": "Appointment rescheduled successfully",
                "new_date": new_date,
                "new_token": appt.token_number
            }, status=status.HTTP_200_OK)
