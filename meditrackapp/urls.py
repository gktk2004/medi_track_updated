from django.urls import path
from.import views
from .views import *

urlpatterns = [
    path('',views.login,name='login'),
    path('admin_index',views.admin_index,name='admin_index'),
    path('doctor_index',views.doctor_index,name='doctor_index'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    path('manage_doctor/', views.manage_doctor, name='manage_doctor'),
    path('add_doctor',views.add_doctor,name='add_doctor'),
    path('view_doctors',views.view_doctors,name='view_doctors'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/profile/update/', views.doctor_update_profile, name='doctor_update_profile'),
    path('approve-doctor/<int:doctor_id>/', views.approve_doctor, name='approve_doctor'),
    path('reject-doctor/<int:doctor_id>/', views.reject_doctor, name='reject_doctor'),
    path('view_approved_doctors/', views.view_approved_doctors, name='view_approved_doctors'),
    path('view_rejected_doctors/', views.view_rejected_doctors, name='view_rejected_doctors'),
    path('upcoming_appointments/', views.doctor_upcoming_appointments, name='upcoming_appointments'),
]