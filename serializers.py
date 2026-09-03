from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    Salon,
    Service,
    Staff,
    Availability,
    Appointment,
    Review,
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):
        if UserProfile.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        if User.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        name = validated_data['name']
        email = validated_data['email']

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        profile = UserProfile.objects.create(
            user=user,
            name=name,
            email=email,
            role='customer',
        )

        return profile


class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True
    )

    service_name = serializers.CharField(
        source='service.name',
        read_only=True
    )

    salon_name = serializers.CharField(
        source='salon.name',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer',
            'customer_name',
            'salon',
            'salon_name',
            'service',
            'service_name',
            'staff',
            'date',
            'start_time',
            'end_time',
            'status',
            'created_at',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'