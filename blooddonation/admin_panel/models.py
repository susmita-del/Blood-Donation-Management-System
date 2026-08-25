# Create your models here.
# from system.models import Donor
from django.contrib.auth.models import User
from django.db import models

BLOOD_GROUPS = [
    ("O+", "O+"), ("O-", "O-"), ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"),
]

class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="donor_profile")
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')])
    phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, default="O+")
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    available_to_donate = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.blood_group})"


class BloodRequest(models.Model):
    URGENCY = [("Normal", "Normal"), ("Urgent", "Urgent"), ("Critical", "Critical")]
    STATUS = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected"), ("Completed", "Completed")]

    patient_name = models.CharField(max_length=120)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blood_requests")
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    hospital_name = models.CharField(max_length=150)
    city = models.CharField(max_length=80)
    urgency = models.CharField(max_length=20, choices=URGENCY, default="Normal")
    additional_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group}"


class Donation(models.Model):
    STATUS = [("Scheduled", "Scheduled"), ("Completed", "Completed"), ("Cancelled", "Cancelled")]
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name="donations")
    hospital = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    donation_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default="Completed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor} - {self.donation_date}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

