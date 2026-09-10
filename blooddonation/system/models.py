from admin_panel.models import DonorProfile

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Donor(models.Model):  # Capital D
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # login er sathe connect
    name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female')])
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True) # Available kina
    last_donated = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.blood_group}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email
class BloodRequest(models.Model):
    patient_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group}"


# old code
# class DonorRegistration(models.Model):  # Donor noy, DonorRegistration
#     name = models.CharField(max_length=100)
#     age = models.IntegerField()
#     gender = models.CharField(max_length=10)
#     blood_group = models.CharField(max_length=5)
#     phone = models.CharField(max_length=15)
#     email = models.EmailField(blank=True)
#     state = models.CharField(max_length=100)
#     city = models.CharField(max_length=100)
#     last_donation = models.DateField(null=True, blank=True)
#     address = models.TextField(blank=True)


# new code added

class DonorRegistration(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='donor_registration'
    )

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    last_donation = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    
    def __str__(self):
        return f"{self.name} - {self.blood_group}"