from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Donor

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
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            error = "Passwords do not match"
        elif User.objects.filter(email=email).exists():
            error = "Email already exists"
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        
            success = "Registration Successful! Please Login."
            
    return render(request, 'register.html', {'error': error, 'success': success})






def search_donor(request):
    doner = Donor.objects.filter(is_available=True)
    
    # Filter logic
    blood_group = request.GET.get('blood_group')
    state = request.GET.get('state')
    city = request.GET.get('city')
    
    if blood_group:
        doner = doner.filter(blood_group=blood_group)
    if state:
        doner = doner.filter(state=state)
    if city:
        doner = doner.filter(city=city)

    context = {'doner': doner}
    return render(request, 'doner.html', context)