from django.urls import path

from .views import (
    register,
    user_list,
    my_profile,
    salon_list,
    service_list,
    staff_list,
    availability_list,
    appointment_list,
    my_appointments,
    cancel_appointment,
    review_list,
    owner_dashboard,
    update_appointment_status,
    admin_dashboard,
)


urlpatterns = [

    path(
        'register/',
        register
    ),

    path(
        'users/',
        user_list
    ),

    path(
        'my-profile/',
        my_profile
    ),

    path(
        'salons/',
        salon_list
    ),

    path(
        'services/',
        service_list
    ),

    path(
        'staff/',
        staff_list
    ),

    path(
        'availability/',
        availability_list
    ),

    path(
        'appointments/',
        appointment_list
    ),

    path(
        'my-appointments/',
        my_appointments
    ),

    path(
        'appointments/<int:appointment_id>/cancel/',
        cancel_appointment
    ),

    path(
        'appointments/<int:appointment_id>/status/',
        update_appointment_status
    ),

    path(
        'reviews/',
        review_list
    ),

    path(
        'owner-dashboard/',
        owner_dashboard
    ),

    path(
        'admin-dashboard/',
        admin_dashboard
    ),
]