from django.contrib import admin

# Register your models here.
from .models import Donor
admin.site.register(Donor)
from .models import BloodRequest

admin.site.register(BloodRequest)


from .models import DonorRegistration

@admin.register(DonorRegistration)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'phone', 'city' )
    list_filter = ('blood_group', 'city')
    search_fields = ('name', 'phone')