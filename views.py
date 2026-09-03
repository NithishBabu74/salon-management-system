from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    UserProfile,
    Salon,
    Service,
    Staff,
    Availability,
    Appointment,
    Review,
)

from .serializers import (
    UserProfileSerializer,
    RegisterSerializer,
    SalonSerializer,
    ServiceSerializer,
    StaffSerializer,
    AvailabilitySerializer,
    AppointmentSerializer,
    ReviewSerializer,
)


# =========================================================
# REGISTER
# =========================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        profile = serializer.save()

        return Response(
            {
                'message': 'Registration successful.',
                'user': UserProfileSerializer(profile).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# USERS
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def user_list(request):

    users = UserProfile.objects.all().order_by('id')

    serializer = UserProfileSerializer(
        users,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# MY PROFILE
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:
        return Response(
            {'error': 'Profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserProfileSerializer(profile)

    return Response(serializer.data)


# =========================================================
# SALONS
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def salon_list(request):

    salons = Salon.objects.all().order_by('id')

    serializer = SalonSerializer(
        salons,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# SERVICES
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request):

    services = Service.objects.all().order_by('id')

    serializer = ServiceSerializer(
        services,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# STAFF
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def staff_list(request):

    staff = Staff.objects.all().order_by('id')

    serializer = StaffSerializer(
        staff,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# AVAILABILITY
# =========================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def availability_list(request):

    availability = Availability.objects.all().order_by('id')

    serializer = AvailabilitySerializer(
        availability,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# APPOINTMENTS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list(request):

    # ---------------- GET ----------------

    if request.method == 'GET':

        appointments = Appointment.objects.all().order_by(
            'date',
            'start_time'
        )

        serializer = AppointmentSerializer(
            appointments,
            many=True
        )

        return Response(serializer.data)

    # ---------------- POST ----------------

    try:

        # Find logged-in customer profile
        profile = UserProfile.objects.filter(
            user=request.user
        ).first()

        if not profile:
            profile = UserProfile.objects.filter(
                email__iexact=request.user.email
            ).first()

        if not profile:
            return Response(
                {'error': 'Customer profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get booking data
        service_id = request.data.get('service')
        salon_id = request.data.get('salon')
        staff_id = request.data.get('staff')
        date_value = request.data.get('date')
        start_time_value = request.data.get('start_time')
        end_time_value = request.data.get('end_time')

        # Check required fields
        if not all([
            service_id,
            salon_id,
            staff_id,
            date_value,
            start_time_value,
            end_time_value
        ]):

            return Response(
                {'error': 'All booking details are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- DATE ----------------

        try:

            booking_date = datetime.strptime(
                str(date_value).strip(),
                '%Y-%m-%d'
            ).date()

        except (ValueError, TypeError):

            return Response(
                {
                    'error': 'Invalid date format. Use YYYY-MM-DD.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- START TIME ----------------

        try:

            start_text = str(
                start_time_value
            ).strip()

            if len(start_text) == 5:

                start_time = datetime.strptime(
                    start_text,
                    '%H:%M'
                ).time()

            else:

                start_time = datetime.strptime(
                    start_text,
                    '%H:%M:%S'
                ).time()

        except (ValueError, TypeError):

            return Response(
                {'error': 'Invalid start time format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- END TIME ----------------

        try:

            end_text = str(
                end_time_value
            ).strip()

            if len(end_text) == 5:

                end_time = datetime.strptime(
                    end_text,
                    '%H:%M'
                ).time()

            else:

                end_time = datetime.strptime(
                    end_text,
                    '%H:%M:%S'
                ).time()

        except (ValueError, TypeError):

            return Response(
                {'error': 'Invalid end time format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- PAST DATE ----------------

        today = timezone.localdate()

        if booking_date < today:

            return Response(
                {'error': 'Cannot book a past date.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- GET OBJECTS ----------------

        try:

            service_obj = Service.objects.get(
                id=service_id
            )

            salon_obj = Salon.objects.get(
                id=salon_id
            )

            staff_obj = Staff.objects.get(
                id=staff_id
            )

        except Service.DoesNotExist:

            return Response(
                {'error': 'Selected service not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Salon.DoesNotExist:

            return Response(
                {'error': 'Selected salon not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Staff.DoesNotExist:

            return Response(
                {'error': 'Selected stylist not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- STAFF + SALON CHECK ----------------

        if staff_obj.salon_id != salon_obj.id:

            return Response(
                {
                    'error':
                    'Selected stylist does not belong to this salon.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- SERVICE + SALON CHECK ----------------

        if service_obj.salon_id != salon_obj.id:

            return Response(
                {
                    'error':
                    'Selected service does not belong to this salon.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- TIME CHECK ----------------

        if end_time <= start_time:

            return Response(
                {
                    'error':
                    'End time must be after start time.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- STAFF AVAILABILITY ----------------

        day_name = booking_date.strftime('%A')

        availability = Availability.objects.filter(
            staff=staff_obj,
            day__iexact=day_name
        ).first()

        if not availability:

            return Response(
                {
                    'error':
                    f'Stylist is not available on {day_name}.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            start_time < availability.start_time
            or
            end_time > availability.end_time
        ):

            return Response(
                {
                    'error':
                    (
                        f'Stylist is available from '
                        f'{availability.start_time.strftime("%H:%M")} '
                        f'to '
                        f'{availability.end_time.strftime("%H:%M")}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- OVERLAPPING BOOKING CHECK ----------------

        overlapping = Appointment.objects.filter(
            staff=staff_obj,
            date=booking_date,
            status='confirmed',
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping:

            return Response(
                {
                    'error':
                    'This time slot is already booked.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------- CREATE APPOINTMENT ----------------

        appointment = Appointment.objects.create(
            customer=profile,
            salon=salon_obj,
            service=service_obj,
            staff=staff_obj,
            date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )

        serializer = AppointmentSerializer(
            appointment
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# MY APPOINTMENTS
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:

        return Response(
            {'error': 'Customer profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    appointments = Appointment.objects.filter(
        customer=profile
    ).order_by(
        'date',
        'start_time'
    )

    serializer = AppointmentSerializer(
        appointments,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# CANCEL APPOINTMENT
# =========================================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:

        return Response(
            {'error': 'Customer profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:

        appointment = Appointment.objects.get(
            id=appointment_id
        )

    except Appointment.DoesNotExist:

        return Response(
            {'error': 'Appointment not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check ownership
    if appointment.customer_id != profile.id:

        return Response(
            {
                'error':
                'You can cancel only your own appointment.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Already cancelled
    if appointment.status == 'cancelled':

        return Response(
            {
                'error':
                'Appointment is already cancelled.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check past appointment
    appointment_datetime = timezone.make_aware(
        datetime.combine(
            appointment.date,
            appointment.start_time
        )
    )

    if appointment_datetime <= timezone.now():

        return Response(
            {
                'error':
                'Past appointment cannot be cancelled.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = 'cancelled'

    appointment.save()

    serializer = AppointmentSerializer(
        appointment
    )

    return Response(serializer.data)


# =========================================================
# REVIEWS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_list(request):

    if request.method == 'GET':

        reviews = Review.objects.all().order_by(
            '-created_at'
        )

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)

    serializer = ReviewSerializer(
        data=request.data
    )

    if serializer.is_valid():

        review = serializer.save()

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# OWNER DASHBOARD
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_dashboard(request):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:

        return Response(
            {'error': 'Profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Owner / Admin only
    if profile.role not in ['salon_owner', 'admin']:

        return Response(
            {
                'error':
                'You do not have permission to access owner dashboard.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    salon = Salon.objects.first()

    if not salon:

        return Response(
            {'error': 'Salon not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    appointments = Appointment.objects.filter(
        salon=salon
    ).order_by(
        'date',
        'start_time'
    )

    staff = Staff.objects.filter(
        salon=salon
    ).order_by('id')

    services = Service.objects.filter(
        salon=salon
    ).order_by('id')

    total_customers = Appointment.objects.filter(
        salon=salon
    ).values(
        'customer'
    ).distinct().count()

    stats = {
        'total_appointments':
            appointments.count(),

        'confirmed_appointments':
            appointments.filter(
                status='confirmed'
            ).count(),

        'cancelled_appointments':
            appointments.filter(
                status='cancelled'
            ).count(),

        'completed_appointments':
            appointments.filter(
                status='completed'
            ).count(),

        'total_customers':
            total_customers,

        'total_staff':
            staff.count(),

        'total_services':
            services.count(),
    }

    return Response(
        {
            'salon': SalonSerializer(salon).data,

            'stats': stats,

            'appointments':
                AppointmentSerializer(
                    appointments,
                    many=True
                ).data,

            'staff':
                StaffSerializer(
                    staff,
                    many=True
                ).data,

            'services':
                ServiceSerializer(
                    services,
                    many=True
                ).data,
        }
    )


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_appointment_status(
    request,
    appointment_id
):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:

        return Response(
            {'error': 'Profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if profile.role not in ['salon_owner', 'admin']:

        return Response(
            {
                'error':
                'You do not have permission.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:

        appointment = Appointment.objects.get(
            id=appointment_id
        )

    except Appointment.DoesNotExist:

        return Response(
            {
                'error':
                'Appointment not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get(
        'status'
    )

    allowed_statuses = [
        'confirmed',
        'cancelled',
        'completed'
    ]

    if new_status not in allowed_statuses:

        return Response(
            {
                'error':
                'Invalid status.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = new_status

    appointment.save()

    serializer = AppointmentSerializer(
        appointment
    )

    return Response(serializer.data)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        profile = UserProfile.objects.filter(
            email__iexact=request.user.email
        ).first()

    if not profile:

        return Response(
            {'error': 'Profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Admin only
    if profile.role != 'admin':

        return Response(
            {
                'error':
                'Admin access required.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    users = UserProfile.objects.all().order_by('id')

    salons = Salon.objects.all().order_by('id')

    appointments = Appointment.objects.all().order_by(
        'date',
        'start_time'
    )

    stats = {

        'total_users':
            UserProfile.objects.count(),

        'total_salons':
            Salon.objects.count(),

        'total_services':
            Service.objects.count(),

        'total_staff':
            Staff.objects.count(),

        'total_appointments':
            Appointment.objects.count(),

        'confirmed_appointments':
            Appointment.objects.filter(
                status='confirmed'
            ).count(),

        'cancelled_appointments':
            Appointment.objects.filter(
                status='cancelled'
            ).count(),

        'completed_appointments':
            Appointment.objects.filter(
                status='completed'
            ).count(),
    }

    return Response(
        {
            'stats': stats,

            'users':
                UserProfileSerializer(
                    users,
                    many=True
                ).data,

            'salons':
                SalonSerializer(
                    salons,
                    many=True
                ).data,

            'appointments':
                AppointmentSerializer(
                    appointments,
                    many=True
                ).data,
        }
    )