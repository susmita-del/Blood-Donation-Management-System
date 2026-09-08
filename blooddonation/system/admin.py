from django.contrib import admin

# Register your models here.
from .models import Donor
admin.site.register(Donor)
from .models import BloodRequest

admin.site.register(BloodRequest)