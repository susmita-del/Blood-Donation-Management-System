from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import BLOOD_GROUPS, BloodRequest, Donation, DonorProfile, Notification


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url="admin_panel:login")
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("user_dashboard:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    if request.user.is_authenticated:
        return redirect("admin_panel:dashboard" if request.user.is_staff else "user_dashboard:dashboard")
    return redirect("admin_panel:login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("admin_panel:dashboard" if request.user.is_staff else "user_dashboard:dashboard")

    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Please contact the administrator.")
                return redirect("admin_panel:login")
            login(request, user)
            next_url = request.POST.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("admin_panel:dashboard" if user.is_staff else "user_dashboard:dashboard")

        messages.error(request, "Invalid username/email or password.")
        return redirect("admin_panel:login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("admin_panel:login")


@staff_required
def dashboard(request):
    total_donors = DonorProfile.objects.count()
    total_requests = BloodRequest.objects.count()
    completed_donations = Donation.objects.filter(status="Completed").count()
    pending_requests = BloodRequest.objects.filter(status="Pending").count()
    approved_requests_count = BloodRequest.objects.filter(status="Approved").count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    blood_counts = {
        group: Donation.objects.filter(blood_group=group, status="Completed").count()
        for group, _ in BLOOD_GROUPS
    }

    activities = []
    for item in BloodRequest.objects.select_related("requester").order_by("-created_at")[:6]:
        activities.append({
            "icon": "droplet",
            "text": f"Blood request received for {item.blood_group}",
            "sub": item.patient_name,
            "time": item.created_at,
        })
    for donor in DonorProfile.objects.select_related("user").order_by("-joined_at")[:6]:
        activities.append({
            "icon": "user-plus",
            "text": "New donor registered",
            "sub": donor.user.get_full_name() or donor.user.username,
            "time": donor.joined_at,
        })
    activities.sort(key=lambda x: x["time"], reverse=True)

    return render(request, "dashboard.html", {
        "total_donors": total_donors,
        "total_requests": total_requests,
        "completed_donations": completed_donations,
        "pending_requests": pending_requests,
        "approved_requests_count": approved_requests_count,
        "blood_counts": blood_counts,
        "activities": activities[:6],
        "unread_notifications": unread_notifications,
        "active": "dashboard",
    })


@staff_required
def donors(request):
    q = request.GET.get("q", "").strip()
    group = request.GET.get("blood_group", "")
    available = request.GET.get("available", "")
    qs = DonorProfile.objects.select_related("user").order_by("-joined_at")
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q) | Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) | Q(city__icontains=q)
        )
    if group:
        qs = qs.filter(blood_group=group)
    if available == "yes":
        qs = qs.filter(available_to_donate=True)
    return render(request, "donors.html", {
        "donors": qs, "groups": BLOOD_GROUPS, "q": q,
        "selected_group": group, "available": available, "active": "donors",
    })


@staff_required
def donor_detail(request, pk):
    donor = get_object_or_404(DonorProfile.objects.select_related("user"), pk=pk)
    donations = donor.donations.order_by("-donation_date")
    return render(request, "donor_detail.html", {"donor": donor, "donations": donations, "active": "donors"})


# @staff_required
# def requests_page(request):
#     status = request.GET.get("status", "")
#     urgency = request.GET.get("urgency", "")
#     qs = BloodRequest.objects.select_related("requester", "assigned_donor__user").order_by("-created_at")
#     if status:
#         qs = qs.filter(status=status)
#     if urgency:
#         qs = qs.filter(urgency=urgency)
#     return render(request, "requests.html", {
#         "requests": qs, "selected_status": status, "selected_urgency": urgency, "active": "requests",
#     })

@staff_required
def requests_page(request):

    status = request.GET.get("status", "")
    urgency = request.GET.get("urgency", "")

    qs = BloodRequest.objects.select_related(
        "requester",
        "assigned_donor__user"
    ).order_by("-created_at")

    if status:
        qs = qs.filter(status=status)

    if urgency:
        qs = qs.filter(urgency=urgency)

    # Prepare matching donors for every request
    for blood_request in qs:

        blood_request.available_donors = DonorProfile.objects.filter(
            blood_group=blood_request.blood_group,
            available_to_donate=True,
            user__is_active=True
        ).exclude(
            user=blood_request.requester
        ).order_by("name")

    return render(
        request,
        "requests.html",
        {
            "requests": qs,
            "selected_status": status,
            "selected_urgency": urgency,
            "active": "requests",
        }
    )


def _notify_donors(blood_request):
    donors = DonorProfile.objects.select_related("user").filter(
        blood_group=blood_request.blood_group,
        available_to_donate=True,
        city__iexact=blood_request.city,
        user__is_active=True,
    ).exclude(user=blood_request.requester)

    # If there are no city matches, fall back to all matching available donors.
    if not donors.exists():
        donors = DonorProfile.objects.select_related("user").filter(
            blood_group=blood_request.blood_group,
            available_to_donate=True,
            user__is_active=True,
        ).exclude(user=blood_request.requester)

    blood_request.notified_donors.add(*donors)
    Notification.objects.bulk_create([        Notification(
            user=donor.user,
            message=(
                f"New {blood_request.urgency.lower()} {blood_request.blood_group} blood request "
                f"for {blood_request.patient_name} at {blood_request.hospital_name} ({blood_request.city})."
            ),
        )
        for donor in donors
    ])
    return donors


@staff_required
def approve_request(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:requests")
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    if blood_request.status != "Pending":
        messages.warning(request, "This request has already been reviewed.")
        return redirect("admin_panel:requests")

    blood_request.status = "Approved"
    blood_request.reviewed_at = timezone.now()
    blood_request.donor_response = "Waiting"
    blood_request.save(update_fields=["status", "reviewed_at", "donor_response"])

    Notification.objects.create(
        user=blood_request.requester,
        message=f"Your {blood_request.blood_group} blood request has been approved and is being matched with donors.",
    )
    donors = _notify_donors(blood_request)
    messages.success(request, f"Request for {blood_request.patient_name} approved. {donors.count()} matching donor(s) notified.")
    return redirect("admin_panel:requests")

@staff_required
def assign_donor(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:requests")

    blood_request = get_object_or_404(
        BloodRequest,
        pk=pk
    )

    donor_id = request.POST.get("donor_id")

    if not donor_id:
        messages.error(
            request,
            "Please select a donor."
        )
        return redirect("admin_panel:requests")

    donor = get_object_or_404(
        DonorProfile,
        pk=donor_id,
        available_to_donate=True,
        blood_group=blood_request.blood_group
    )

    # Assign donor
    blood_request.assigned_donor = donor
    blood_request.donor_response = "Waiting"

    blood_request.save(
        update_fields=[
            "assigned_donor",
            "donor_response"
        ]
    )

    # Notify donor
    Notification.objects.create(
        user=donor.user,
        message=(
            f"You have been assigned a {blood_request.blood_group} "
            f"blood request for {blood_request.patient_name} "
            f"at {blood_request.hospital_name}. "
            f"Please review and accept or decline."
        )
    )

    # Notify receiver
    Notification.objects.create(
        user=blood_request.requester,
        message=(
            f"A donor has been assigned to your "
            f"{blood_request.blood_group} blood request."
        )
    )

    messages.success(
        request,
        f"{donor.name} has been assigned successfully."
    )

    return redirect("admin_panel:requests")


@staff_required
def reject_request(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:requests")
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    blood_request.status = "Rejected"
    blood_request.reviewed_at = timezone.now()
    blood_request.donor_response = "Waiting"
    blood_request.save(update_fields=["status", "reviewed_at", "donor_response"])
    Notification.objects.create(
        user=blood_request.requester,
        message=f"Your blood request for {blood_request.blood_group} has been rejected by the administrator.",
    )
    messages.warning(request, f"Request for {blood_request.patient_name} rejected.")
    return redirect("admin_panel:requests")


@staff_required
def approved_requests(request):
    qs = BloodRequest.objects.filter(status="Approved").select_related("requester", "assigned_donor__user").order_by("-reviewed_at")
    return render(request, "approved_requests.html", {"requests": qs, "active": "approved"})


@staff_required
def users(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.order_by("-date_joined")
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    return render(request, "users.html", {"users": qs, "q": q, "active": "users"})


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
        "active": "reports",
    })


@staff_required
def notifications(request):
    items = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications.html", {"notifications": items, "active": "notifications"})


@staff_required
def mark_notification_read(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:notifications")
    item = get_object_or_404(Notification, pk=pk, user=request.user)
    item.is_read = True
    item.save(update_fields=["is_read"])
    return redirect("admin_panel:notifications")


@staff_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect("admin_panel:notifications")


@staff_required
def donations(request):
    qs = Donation.objects.select_related("donor__user", "request__requester").order_by("-donation_date", "-created_at")
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    return render(request, "donations.html", {"donations": qs, "selected_status": status, "active": "donations"})


@staff_required
def complete_donation(request, pk):
    if request.method != "POST":
        return redirect("admin_panel:donations")
    donation = get_object_or_404(Donation.objects.select_related("donor__user", "request"), pk=pk)
    if donation.status != "Scheduled":
        messages.warning(request, "Only scheduled donations can be completed.")
        return redirect("admin_panel:donations")

    donation.status = "Completed"
    donation.save(update_fields=["status"])
    donation.donor.last_donation_date = donation.donation_date
    donation.donor.available_to_donate = False
    donation.donor.save(update_fields=["last_donation_date", "available_to_donate"])

    if donation.request_id:
        blood_request = donation.request
        blood_request.status = "Completed"
        blood_request.save(update_fields=["status"])
        Notification.objects.create(
            user=blood_request.requester,
            message=f"Donation for your {blood_request.blood_group} request has been completed by the donor."
        )

    Notification.objects.create(
        user=donation.donor.user,
        message=f"Your donation at {donation.hospital} on {donation.donation_date:%d %b %Y} has been marked completed. Thank you!"
    )
    messages.success(request, "Donation marked as completed.")
    return redirect("admin_panel:donations")
