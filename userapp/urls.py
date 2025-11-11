from django.urls import path
from django.urls import path, re_path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from .views import *

schema_view = get_schema_view(
    openapi.Info(
        title="MEDITRACK API",
        default_version="v1",
        description="API documentation for the Meditrack system.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@PETCURE.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],

)

router = DefaultRouter()
router.register(r"user_registration",UserRegistrationView),

urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("",include(router.urls)),
    path('login/', LoginView.as_view(), name='user_login'),
    path('view_profile/',UserProfileView.as_view({'get':'list'}),name='view_profile'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('available_doctors/', AvailableDoctorsView.as_view(), name='available_doctors'),
    path('expected_token/', ExpectedTokenNumberView.as_view(), name='expected_token'),
    path('book_appointment/', AppointmentBookingView.as_view(), name='book_appointment'),
    path('card_payment/',CardPaymentView.as_view(),name='card_payment'),
    path('upi_payment/',UPIPaymentView.as_view(),name='upi_payment'),
    path('appointments/', UserAppointmentListView.as_view(), name='user-appointments'),
    path('appointment_details/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('cancel_appointment/', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('prescriptions/', UserPrescriptionsView.as_view(), name='user_prescriptions'),
    path('prescription_details/', PrescriptionDetailView.as_view(), name='prescription_details'),
    path('submit_feedback/', SubmitFeedbackView.as_view(), name='submit_feedback'),
    path('feedback_list/', FeedbackListView.as_view(), name='feedback_list'),
    path('feedback_details/', FeedbackDetailView.as_view(), name='feedback_details'),
    path('appointment_confirmation/', BookingConfirmationView.as_view(), name='booking_confirmation'),
]
