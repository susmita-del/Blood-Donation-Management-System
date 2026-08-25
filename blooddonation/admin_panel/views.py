from functools import wraps
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import DonorProfile, BloodRequest, Donation, Notification, BLOOD_GROUPS


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url="login")
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Acess Denied. Admin only .")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_panel:dashboard")
    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        # Admin -> Dashboard
        if request.user.is_staff:
            return redirect("admin_panel:dashboard")
        
       # Normal user -> Logout and back to login
        messages.error(request, "You do not have access.")
        logout(request)
        return redirect("login")

    # LOGIN FORM SUBMISSION
    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        password = request.POST.get("password", "")
        user=None

        # TRY USERNAME
        user = authenticate(request, username=username_or_email, password=password)

        # If username fails, try email
        if user is None:
            try:
                user_obj=User.objects.get(email__iexact=username_or_email)
                user=authenticate(request,username=user_obj.username,password=password)
            except User.DoesNotExist:
                user=None

     # CHECK AUTHENTICATION
        if user is not None:
            
                 # Important admin check
           if user.is_staff:
              login(request, user)
              next_url = request.POST.get("next")
              if next_url:
                 return redirect(next_url)
              return redirect("admin_panel:dashboard")

           else:
                # Normal user is NOT allowed
                messages.error(request," You are not authorized to access the Admin Dashboard .")
                return redirect("login")
        else:
            messages.error(request, "Invalid username/email or password.")
            return redirect("login")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@staff_required
def dashboard(request):
    total_donors = DonorProfile.objects.count()
    total_requests = BloodRequest.objects.count()
    completed_donations = Donation.objects.filter(status="Completed").count()
    pending_requests = BloodRequest.objects.filter(status="Pending").count()
    approved_requests_count = BloodRequest.objects.filter(status="Approved").count()

    blood_counts = {}
    for group, _ in BLOOD_GROUPS:
        blood_counts[group] = Donation.objects.filter(
            blood_group=group, status="Completed"
        ).count()

    activities = []
    for item in BloodRequest.objects.select_related("requester").order_by("-created_at")[:4]:
        activities.append({
            "icon": "droplet",
            "text": f"Blood request received for {item.blood_group}",
            "sub": item.patient_name,
            "time": item.created_at,
        })
    for donor in DonorProfile.objects.select_related("user").order_by("-joined_at")[:4]:
        activities.append({
            "icon": "user-plus",
            "text": "New donor registered",
            "sub": donor.user.get_full_name() or donor.user.username,
            "time": donor.joined_at,
        })
    activities.sort(key=lambda x: x["time"], reverse=True)

    context = {
        "total_donors": total_donors,
        "total_requests": total_requests,
        "completed_donations": completed_donations,
        "pending_requests": pending_requests,
        "approved_requests_count": approved_requests_count,
        "blood_counts": blood_counts,
        "activities": activities[:6],
    }
    return render(request, "dashboard.html", context)


@staff_required
def donors(request):
    q = request.GET.get("q", "").strip()
    group = request.GET.get("blood_group", "")
    available = request.GET.get("available", "")

    qs = DonorProfile.objects.select_related("user").order_by("-joined_at")
    if q:
        qs = qs.filter(Q(user__username__icontains=q) | Q(user__first_name__icontains=q) |
                       Q(user__last_name__icontains=q) | Q(city__icontains=q))
    if group:
        qs = qs.filter(blood_group=group)
    if available == "yes":
        qs = qs.filter(available_to_donate=True)

    return render(request, "donors.html", {
        "donors": qs,
        "groups": BLOOD_GROUPS,
        "q": q,
        "selected_group": group,
        "available": available,
    })


@staff_required
def donor_detail(request, pk):
    donor = get_object_or_404(DonorProfile.objects.select_related("user"), pk=pk)
    donations = donor.donations.order_by("-donation_date")
    return render(request, "donor_detail.html", {"donor": donor, "donations": donations})


@staff_required
def requests_page(request):
    status = request.GET.get("status", "")
    urgency = request.GET.get("urgency", "")
    qs = BloodRequest.objects.select_related("requester").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    if urgency:
        qs = qs.filter(urgency=urgency)
    return render(request, "requests.html", {
        "requests": qs,
        "selected_status": status,
        "selected_urgency": urgency,
    })


@staff_required
def approve_request(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:requests")
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    blood_request.status = "Approved"
    blood_request.reviewed_at = timezone.now()
    blood_request.save(update_fields=["status", "reviewed_at"])
    Notification.objects.create(
        user=blood_request.requester,
        message=f"Your blood request for {blood_request.blood_group} has been approved."
    )
    messages.success(request, f"Request for {blood_request.patient_name} approved.")
    return redirect("admin_panel:requests")


@staff_required
def reject_request(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:requests")
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    blood_request.status = "Rejected"
    blood_request.reviewed_at = timezone.now()
    blood_request.save(update_fields=["status", "reviewed_at"])
    Notification.objects.create(
        user=blood_request.requester,
        message=f"Your blood request for {blood_request.blood_group} has been rejected."
    )
    messages.warning(request, f"Request for {blood_request.patient_name} rejected.")
    return redirect("admin_panel:requests")


@staff_required
def approved_requests(request):
    qs = BloodRequest.objects.filter(status="Approved").select_related("requester").order_by("-reviewed_at")
    return render(request, "approved_requests.html", {"requests": qs})


@staff_required
def users(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.order_by("-date_joined")
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) |
                       Q(last_name__icontains=q) | Q(email__icontains=q))
    return render(request, "users.html", {"users": qs, "q": q})


@staff_required
def toggle_user(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:users")
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot disable your own admin account.")
        return redirect("admin_panel:users")
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    messages.success(request, f"{user.username} is now {'active' if user.is_active else 'inactive'}.")
    return redirect("admin_panel:users")


@staff_required
def reports(request):
    group_stats = []
    for group, _ in BLOOD_GROUPS:
        group_stats.append({
            "group": group,
            "donors": DonorProfile.objects.filter(blood_group=group).count(),
            "requests": BloodRequest.objects.filter(blood_group=group).count(),
            "donations": Donation.objects.filter(blood_group=group, status="Completed").count(),
        })
    return render(request, "reports.html", {
        "group_stats": group_stats,
        "total_donors": DonorProfile.objects.count(),
        "total_requests": BloodRequest.objects.count(),
        "approved": BloodRequest.objects.filter(status="Approved").count(),
        "completed": Donation.objects.filter(status="Completed").count(),
    })
