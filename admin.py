from django.contrib import admin
from .models import UserProfile, Salon, Service, Staff, Availability, Appointment, Review

admin.site.register(UserProfile)
admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Staff)
admin.site.register(Availability)
admin.site.register(Appointment)
admin.site.register(Review)