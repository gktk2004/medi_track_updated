from django.shortcuts import get_object_or_404, render,redirect
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
    
    
class AvailableDoctorsView(APIView):
    def get(self, request):
        department_id = request.query_params.get('department_id')
        date_str = request.query_params.get('date')

        if not department_id or not date_str:
            return Response(
                {"error": "department_id and date are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and convert date
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get weekday name (monday, tuesday, etc.)
        day_name = date_obj.strftime('%A').lower()

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter doctors who belong to department and work on that day
        doctors = Doctor.objects.filter(
            specialization=department,
            working_days__icontains=day_name,
            is_approved=True
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
        
        
class AppointmentDetailView(APIView):
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')

        if not appointment_id:
            return Response(
                {"success": False, "message": "appointment_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment = get_object_or_404(Appointment, id=appointment_id)
        serializer = AppointmentDetailSerializer(appointment)

        return Response({
            "success": True,
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