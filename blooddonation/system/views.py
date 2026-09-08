from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Donor
from .models import BloodRequest

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




def search_donor(request):
    doner = Donor.objects.filter(is_available=True)

    blood_group = request.GET.get('blood_group')
    state = request.GET.get('state')
    city = request.GET.get('city')

    # Select thakle filter korbe na
    if blood_group and blood_group != "Select":
        doner = doner.filter(blood_group=blood_group)
    if state and state != "Select" and state != "":
        doner = doner.filter(state__icontains=state)
    if city and city != "Select" and city != "":
        doner = doner.filter(city__icontains=city)

    return render(request, 'doner.html', {'doner': doner})

def blood_request_view(request):
    if request.method == 'POST':
        BloodRequest.objects.create(
            patient_name = request.POST.get('patient_name'),
            hospital_name = request.POST.get('hospital_name'),
            blood_group = request.POST.get('blood_group'),
            city = request.POST.get('city'),
            urgency = request.POST.get('urgency'),
            details = request.POST.get('details'),
        )
        return render(request, 'blood_request.html', {'success': 'Your blood request has been submitted successfully! We will contact donors.'})
    
    return render(request, 'blood_request.html')

def request_list_view(request): # sob request dekhar jonno
    all_requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, 'request_list.html', {'requests': all_requests})