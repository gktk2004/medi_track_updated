from django.urls import path
from django.urls import path, re_path,include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()

urlpatterns = [
    path("",include(router.urls)),
    path('user_registration/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('view_profile/',UserProfileView.as_view({'get':'list'}),name='view_profile'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path(
        'available_doctors/', AvailableDoctorsView.as_view(), name='available_doctors'),
    path('expected_token/', ExpectedTokenNumberView.as_view(), name='expected_token'),
    path('book_appointment/', AppointmentBookingView.as_view(), name='book_appointment'),
    path('card_payment/',CardPaymentView.as_view(),name='card_payment'),
    path('upi_payment/',UPIPaymentView.as_view(),name='upi_payment'),
    path("upcoming_appointments/",UpcomingAppointmentsView.as_view(),name="user_upcoming_appointments_api"),
    path('appointments/', UserAppointmentListView.as_view(), name='user-appointments'),
    path('appointment_details/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('cancel_appointment/', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('prescriptions/', UserPrescriptionsView.as_view(), name='user_prescriptions'),
    path('prescription_details/', PrescriptionDetailView.as_view(), name='prescription_details'),
    path('submit_feedback/', SubmitFeedbackView.as_view(), name='submit_feedback'),
    path('feedback_list/', FeedbackListView.as_view(), name='feedback_list'),
    path('feedback_details/', FeedbackDetailView.as_view(), name='feedback_details'),
    path('appointment_confirmation/', BookingConfirmationView.as_view(), name='booking_confirmation'),
    path("accept-reschedule/", AcceptRescheduleAPIView.as_view(), name="accept_reschedule"),
    path("reject-reschedule/", RejectRescheduleAPIView.as_view(), name="reject_reschedule"),
    path("doctor-reschedule-request/", DoctorRescheduleRequestAPIView.as_view(), name="api_doctor_reschedule_request"),
    path("admin-review-reschedule/", AdminReviewRescheduleAPIView.as_view(), name="admin_review_reschedule"),
    path("user-accept-reschedule/", UserAcceptRescheduleAPIView.as_view(), name="user_accept_reschedule"),
    path("user-reject-reschedule/", UserRejectRescheduleAPIView.as_view(), name="user_reject_reschedule"),
    path("blood-admin-login/", BloodDonationAdminLoginAPIView.as_view(), name="blood_admin_login"),
    path("blood-admin-view-requests/", BloodDonationAdminViewRequestsAPIView.as_view(), name="blood_admin_view_requests"),
    path("blood-admin-approve-request/", BloodDonationAdminApproveRequestAPIView.as_view(), name="blood_admin_approve_request"),
    path("blood-admin-reject-request/", BloodDonationAdminRejectRequestAPIView.as_view(), name="blood_admin_reject_request"),
    path("blood-admin-view-accepted-donors/", BloodDonationAdminViewAcceptedDonorsAPIView.as_view(), name="blood_admin_view_accepted_donors"),
    path("blood-admin-complete-donation/", BloodDonationAdminCompleteDonationAPIView.as_view(), name="blood_admin_complete_donation"),
    path("admin-create-blood-donation-admin/", AdminCreateBloodDonationAdminAPIView.as_view(), name="admin_create_blood_donation_admin"),
    path("admin-manage-blood-donation-admins/", AdminManageBloodDonationAdminsAPIView.as_view(), name="admin_manage_blood_donation_admins"),
    path("admin-deactivate-blood-donation-admin/", AdminDeactivateBloodDonationAdminAPIView.as_view(), name="admin_deactivate_blood_donation_admin"),
    path("blood_donors/", BloodDonorRegisterView.as_view(), name="blood-donor-register"),
    path("notifications/", UserNotificationsView.as_view(), name="user_notifications"),
    path("donor_accept_blood/", AcceptBloodRequestView.as_view(), name="donor_accept_blood"),
    path("add_donation_record/", AddDonationRecordView.as_view(), name="add_donation_record"),
    path("blood_requests/", BloodRequestsForDonorView.as_view(), name="donor_blood_requests"),
    path("all_blood_requests/", CommonBloodRequestListView.as_view(), name="common_blood_requests"),
    path("donor_history/", DonorDonationHistoryView.as_view(), name="donor_donation_history"),
    path("token_status/", DoctorCurrentTokenView.as_view(), name="doctor_token_status"),
    path("appointment_prescription/", AppointmentPrescriptionStatusView.as_view()),
    path("submit_complaints/", SubmitComplaintAPIView.as_view(), name="submit-complaint"),
    path("next-donation-date/", NextDonationDateAPIView.as_view()),
    path("check_available_slots/", CheckAvailableSlotsAPIView.as_view(), name="check-available-slots"),
    path("user/reschedule/action/", UserRescheduleActionView.as_view(), name="user_reschedule_action"),
]
