

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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE) # login er sathe connect
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