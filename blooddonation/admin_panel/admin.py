
# Register your models here.
from django.contrib import admin
from .models import DonorProfile, BloodRequest, Donation, Notification

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group", "city", "state", "available_to_donate")
    list_filter = ("blood_group", "state", "available_to_donate")
    search_fields = ("user__username", "user__first_name", "user__last_name", "city")

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "blood_group", "hospital_name", "urgency", "status", "created_at")
    list_filter = ("blood_group", "urgency", "status")
    search_fields = ("patient_name", "hospital_name", "city")

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "blood_group", "hospital", "donation_date", "status")
    list_filter = ("blood_group", "status")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read",)
