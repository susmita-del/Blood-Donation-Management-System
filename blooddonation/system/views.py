from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Donor
from .models import BloodRequest

# new added
from admin_panel.models import DonorProfile
from admin_panel.models import BloodRequest as AdminBloodRequest
from .models import DonorRegistration

from admin_panel.models import (
    DonorProfile,
    Notification,
    BloodRequest as AdminBloodRequest,
)

from django.contrib.auth.decorators import login_required

# Create your views here.



def home(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')





def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
       
        if user:
            login(request, user)
            return redirect('home') 
        else:
            error = "Invalid Email or Password"
    return render(request, 'login.html', {'error': error})





def register_view(request):
    error = None
    success = None
    if request.method == 'POST':
        first_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            error = "Passwords do not match"
        elif User.objects.filter(email=email).exists():
            error = "Email already exists"
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name)
        
            success = "Registration Successful! Please Login."
        
    return render(request, 'register.html', {'error': error, 'success': success})


# old code
# def search_donor(request):
#     blood_group = request.GET.get('blood_group')
#     state = request.GET.get('state')
#     city = request.GET.get('city')

#     # prothome kichu dekhabe na
#     doner = Donor.objects.none()
    
#     # user jodi sotti search kore, tokhoni filter hobe
#     is_search = False
#     if (blood_group and blood_group != "Select") or (state and state != "Select" and state != "") or (city and city != "Select" and city != ""):
#         is_search = True

#     if is_search:
#         doner = Donor.objects.filter(is_available=True)
#         if blood_group and blood_group != "Select":
#             doner = doner.filter(blood_group=blood_group)
#         if state and state != "Select" and state != "":
#             doner = doner.filter(state__icontains=state)
#         if city and city != "Select" and city != "":
#             doner = doner.filter(city__icontains=city)

#     # jodi search na hoy, tahole faka pathabo
#     if not is_search:
#         doner = None

#     return render(request, 'doner.html', {'doner': doner})



# new code added
def search_donor(request):
    blood_group = request.GET.get('blood_group', '').strip()
    state = request.GET.get('state', '').strip()
    city = request.GET.get('city', '').strip()

    # Search na korle kono donor dekhabe na
    doner = None

    is_search = bool(
        (blood_group and blood_group != "Select") or
        (state and state != "Select") or
        (city and city != "Select")
    )

    if is_search:

        # Logged-in donor/user profile theke donor khujbe
        doner = DonorProfile.objects.filter(
            available_to_donate=True,
            user__is_active=True,
        ).select_related('user')

        if blood_group and blood_group != "Select":
            doner = doner.filter(
                blood_group=blood_group
            )

        if state and state != "Select":
            doner = doner.filter(
                state__icontains=state
            )

        if city and city != "Select":
            doner = doner.filter(
                city__icontains=city
            )

    return render(
        request,
        'doner.html',
        {
            'doner': doner
        }
    )




# old code
# @login_required(login_url='/login/')  # login na korle /login e pathabe
# def blood_request_view(request):
#     if request.method == 'POST':
#         BloodRequest.objects.create(
#             patient_name = request.POST.get('patient_name'),
#             hospital_name = request.POST.get('hospital_name'),
#             blood_group = request.POST.get('blood_group'),
#             city = request.POST.get('city'),
#             urgency = request.POST.get('urgency'),
#             details = request.POST.get('details'),
#         )
#         return render(request, 'blood_request.html', {'success': 'Your blood request has been submitted successfully! We will contact donors.'})
    
#     return render(request, 'blood_request.html')


# new code added
@login_required(login_url='/login/')
def blood_request_view(request):

    if request.method == 'POST':

        patient_name = request.POST.get('patient_name', '').strip()
        hospital_name = request.POST.get('hospital_name', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        city = request.POST.get('city', '').strip()
        urgency_value = request.POST.get('urgency', '').strip()
        details = request.POST.get('details', '').strip()

        # =========================================
        # 1. SYSTEM APP - BloodRequest
        # =========================================

        BloodRequest.objects.create(
            patient_name=patient_name,
            hospital_name=hospital_name,
            blood_group=blood_group,
            city=city,
            urgency=urgency_value,
            details=details,
        )

        # =========================================
        # 2. Convert urgency for Admin model
        # =========================================

        urgency_map = {
            'High - Need within 24 hours': 'Critical',
            'Medium - Need within 2-3 days': 'Urgent',
            'Low': 'Normal',
        }

        admin_urgency = urgency_map.get(
            urgency_value,
            'Normal'
        )

        # =========================================
        # 3. ADMIN PANEL - BloodRequest
        # =========================================

        admin_request = AdminBloodRequest.objects.create(
            patient_name=patient_name,
            requester=request.user,
            blood_group=blood_group,
            hospital_name=hospital_name,
            city=city,
            urgency=admin_urgency,
            additional_details=details,
        )

        # =========================================
        # 4. ADMIN NOTIFICATION
        # =========================================

        staff_users = User.objects.filter(
            is_staff=True,
            is_active=True
        )

        Notification.objects.bulk_create([
            Notification(
                user=admin,
                message=(
                    f"New {admin_request.urgency.lower()} blood request "
                    f"for {admin_request.blood_group} from "
                    f"{request.user.username}."
                )
            )
            for admin in staff_users
        ])

        return render(
            request,
            'blood_request.html',
            {
                'success':
                'Your blood request has been submitted successfully! '
                'We will contact donors.'
            }
        )

    return render(
        request,
        'blood_request.html'
    )
    



def request_list_view(request): # sob request dekhar jonno
    all_requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, 'request_list.html', {'requests': all_requests})




# old code:
# @login_required(login_url='/login/')  # login na korle /login e pathabe
# def become_a_donor(request):
#     if request.method == 'POST':
#         DonorRegistration.objects.create(
#             name=request.POST.get('name'),
#             age=request.POST.get('age'),
#             gender=request.POST.get('gender'),
#             blood_group=request.POST.get('blood_group'),
#             phone=request.POST.get('phone'),
#             email=request.POST.get('email'),
#             state=request.POST.get('state'),
#             city=request.POST.get('city'),
#             last_donation=request.POST.get('last_donation') or None,
#             address=request.POST.get('address')
#         )
#         return render(request, 'become_donor.html', {'success': True})
#     return render(request, 'become_donor.html')



# new code added
@login_required(login_url='/login/')
def become_a_donor(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        state = request.POST.get('state')
        city = request.POST.get('city', '').strip()
        last_donation = request.POST.get('last_donation') or None
        address = request.POST.get('address', '').strip()

        # =========================================
        # 1. SYSTEM - DonorRegistration
        # =========================================

        donor_registration, created = DonorRegistration.objects.update_or_create(
            user=request.user,
            defaults={
                'name': name,
                'age': age,
                'gender': gender,
                'blood_group': blood_group,
                'phone': phone,
                'email': email,
                'state': state,
                'city': city,
                'last_donation': last_donation,
                'address': address,
            }
        )

        # =========================================
        # 2. SYSTEM - Donor
        # =========================================

        Donor.objects.update_or_create(
            user=request.user,
            defaults={
                'name': name,
                'age': age,
                'gender': gender,
                'blood_group': blood_group,
                'state': state,
                'city': city,
                'phone': phone,
                'is_available': True,
                'last_donated': last_donation,
            }
        )

        # =========================================
        # 3. ADMIN PANEL - DonorProfile
        # =========================================

        donor_profile, donor_created = DonorProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'name': name,
                'age': age,
                'gender': gender,
                'phone': phone,
                'blood_group': blood_group,
                'city': city,
                'state': state,
                'available_to_donate': True,
                'last_donation_date': last_donation,
            }
        )

        # =========================================
        # 4. UPDATE USER EMAIL
        # =========================================

        if email:
            request.user.email = email
            request.user.save(update_fields=['email'])

        # =========================================
        # 5. ADMIN NOTIFICATION
        # =========================================

        staff_users = User.objects.filter(
            is_staff=True,
            is_active=True
        )

        if donor_created:
            notification_message = (
                f"New donor registered: {name} "
                f"({blood_group}) from {city}, {state}."
            )
        else:
            notification_message = (
                f"Donor profile updated: {name} "
                f"({blood_group}) from {city}, {state}."
            )

        Notification.objects.bulk_create([
            Notification(
                user=admin,
                message=notification_message
            )
            for admin in staff_users
        ])

        return render(
            request,
            'become_donor.html',
            {'success': True}
        )

    return render(request, 'become_donor.html')