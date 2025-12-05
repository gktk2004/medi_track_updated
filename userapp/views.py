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


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = request.data.get("email")
            password = request.data.get("password")
            
            try:
                user = User.objects.get(email=email)
                if password == user.password:
                    response_data = {
                        "status": "success",
                        "message": "User logged in successfully",
                        "user_id": str(user.id),
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
        total_tokens = Appointment.objects.filter(doctor=doctor, date=date).count()
        expected_token = total_tokens + 1  # token numbers start from 1 daily

        return Response({
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "date": date,
            "expected_token_number": expected_token
        })
        

class AppointmentBookingView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Book an appointment and generate a token number.
        Token starts at 1 for each doctor per day.
        """
        user_id = request.data.get('user')
        doctor_id = request.data.get('doctor')
        date = request.data.get('date')
        symptoms = request.data.get('symptoms', '')

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

        # ✅ Generate next token for this doctor and date
        last_token = Appointment.objects.filter(doctor=doctor, date=date).aggregate(Max('token_number'))['token_number__max']
        next_token = (last_token or 0) + 1

        # ✅ Create appointment
        appointment = Appointment.objects.create(
            user=user,
            doctor=doctor,
            date=date,
            token_number=next_token,
            symptoms=symptoms,
            payment_status='pending',
            status='upcoming'
        )

        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': 'Appointment booked successfully',
            'appointment': serializer.data,
            'token_number': next_token
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
                date=appointment.date
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
                date=appointment.date
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

        serializer = AppointmentSerializer(appointments, many=True)

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

        # Allow cancellation only for upcoming appointments
        if appointment.status != 'upcoming':
            return Response(
                {"success": False, "message": "Only upcoming appointments can be cancelled."},
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
    """
    GET - Retrieve detailed information about a specific feedback entry.
    Params:
        feedback_id (required)
    Response:
        Appointment details + feedback details
    """

    def get(self, request):
        # ✅ Get feedback_id from query params
        feedback_id = request.query_params.get('feedback_id')

        if not feedback_id:
            return Response(
                {"error": "feedback_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Fetch feedback object
        feedback = get_object_or_404(Feedback, id=feedback_id)
        appointment = feedback.appointment
        doctor = appointment.doctor
        user = appointment.user

        # ✅ Build structured response
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
                    "email": doctor.email
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


class BloodDonorRegisterView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = BloodDonorSerializer(data=request.data)
        
        if serializer.is_valid():
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

        # ---------- Filter blood requests ----------
        requests = BloodRequest.objects.filter(
            blood_group=donor.blood_group,
            status="approved"  # only approved ones are meaningful for donor
        ).filter(
            # Do not show past donation dates
            Q(donation_date__gte=today) | Q(donation_date__isnull=True)
        ).order_by("-created_at")

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
    
    
class CommonBloodRequestListView(APIView):

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Fetch all approved & non-expired blood requests
        requests = BloodRequest.objects.filter(
            status="approved"
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
