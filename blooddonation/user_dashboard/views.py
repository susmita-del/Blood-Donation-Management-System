from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from admin_panel.models import BLOOD_GROUPS, BloodRequest, Donation, DonorProfile, Notification


def user_required(view_func):
    @wraps(view_func)
    @login_required(login_url="admin_panel:login")
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect("admin_panel:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def _get_profile(user):
    try:
        return user.donor_profile
    except DonorProfile.DoesNotExist:
        return None


@user_required
def dashboard(request):
    profile = _get_profile(request.user)
    donations = Donation.objects.filter(donor=profile).order_by("-donation_date") if profile else Donation.objects.none()
    requests = BloodRequest.objects.filter(requester=request.user).select_related("assigned_donor__user").order_by("-created_at")
    notifications_qs = Notification.objects.filter(user=request.user)
    donor_requests = BloodRequest.objects.filter(assigned_donor=profile, status="Approved").order_by("-created_at") if profile else BloodRequest.objects.none()

    next_donation = donations.filter(status="Scheduled", donation_date__gte=timezone.localdate()).order_by("donation_date", "donation_time").first()
    context = {
        "profile": profile,
        "total_donations": donations.count(),
        "completed_donations": donations.filter(status="Completed").count(),
        "recent_donations": donations[:5],
        "next_donation": next_donation,
        "my_requests": requests[:5],
        "my_requests_count": requests.count(),
        "pending_requests_count": requests.filter(status="Pending").count(),
        "approved_requests_count": requests.filter(status="Approved").count(),
        "unread_notifications": notifications_qs.filter(is_read=False).count(),
        "pending_donor_requests": donor_requests,
        "blood_group": profile.blood_group if profile else "—",
        "available_to_donate": profile.available_to_donate if profile else False,
    }
    return render(request, "user_dashboard/dashboard.html", context)


@user_required
def profile(request):
    donor = _get_profile(request.user)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        age = request.POST.get("age", "").strip()
        gender = request.POST.get("gender", "").strip()
        phone = request.POST.get("phone", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        available = request.POST.get("available_to_donate") == "on"

        if not name or not age or gender not in {"Male", "Female"} or blood_group not in dict(BLOOD_GROUPS):
            messages.error(request, "Please complete the required profile fields correctly.")
            return redirect("user_dashboard:profile")
        try:
            age_value = int(age)
        except ValueError:
            messages.error(request, "Age must be a valid number.")
            return redirect("user_dashboard:profile")
        if not 18 <= age_value <= 100:
            messages.error(request, "Age must be between 18 and 100.")
            return redirect("user_dashboard:profile")

        first_name, *last_parts = name.split()
        request.user.first_name = first_name
        request.user.last_name = " ".join(last_parts)
        request.user.save(update_fields=["first_name", "last_name"])

        if donor is None:
            donor = DonorProfile.objects.create(
                user=request.user, name=name, age=age_value, gender=gender, phone=phone,
                blood_group=blood_group, city=city, state=state, available_to_donate=available,
            )
        else:
            donor.name = name
            donor.age = age_value
            donor.gender = gender
            donor.phone = phone
            donor.blood_group = blood_group
            donor.city = city
            donor.state = state
            donor.available_to_donate = available
            donor.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("user_dashboard:profile")

    return render(request, "user_dashboard/profile.html", {"profile": donor, "groups": BLOOD_GROUPS})


@user_required
def search_donors(request):
    q = request.GET.get("q", "").strip()
    group = request.GET.get("blood_group", "").strip()
    city = request.GET.get("city", "").strip()


    searched = bool(q or group or city)

    if searched:
        donors = (
            DonorProfile.objects
            .select_related("user")
            .filter(
                available_to_donate=True,
                user__is_active=True,
            )
            .exclude(user=request.user)
        )

        if q:
            donors = donors.filter(
                Q(name__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(city__icontains=q)
                | Q(state__icontains=q)
                | Q(user__username__icontains=q)
            )

        if group:
            donors = donors.filter(blood_group=group)

        if city:
            donors = donors.filter(city__icontains=city)

        # donors = donors.order_by("city", "name")
    else:
        donors = DonorProfile.objects.none()


    return render(request, "user_dashboard/search_donors.html", {
        "donors": donors.order_by("city", "name"), "groups": BLOOD_GROUPS,
        "q": q, "city": city, "selected_group": group,"searched": searched,
    })


@user_required
def request_blood(request):
    if request.method == "POST":
        patient_name = request.POST.get("patient_name", "").strip()
        blood_group = request.POST.get("blood_group", "").strip()
        hospital_name = request.POST.get("hospital_name", "").strip()
        city = request.POST.get("city", "").strip()
        urgency = request.POST.get("urgency", "Normal").strip()
        details = request.POST.get("additional_details", "").strip()
        if not all([patient_name, blood_group, hospital_name, city]) or blood_group not in dict(BLOOD_GROUPS) or urgency not in {"Normal", "Urgent", "Critical"}:
            messages.error(request, "Please fill all required fields correctly.")
            return redirect("user_dashboard:request_blood")

        blood_request = BloodRequest.objects.create(
            patient_name=patient_name, requester=request.user, blood_group=blood_group,
            hospital_name=hospital_name, city=city, urgency=urgency, additional_details=details,
        )

        staff_users = User.objects.filter(is_staff=True, is_active=True)
        Notification.objects.bulk_create([
            Notification(user=admin, message=f"New {blood_request.urgency.lower()} blood request for {blood_request.blood_group} from {request.user.username}.")
            for admin in staff_users
        ])
        messages.success(request, "Blood request submitted. The admin will review it shortly.")
        return redirect("user_dashboard:my_requests")

    return render(request, "user_dashboard/request_blood.html", {"groups": BLOOD_GROUPS})


@user_required
def my_requests(request):
    requests = BloodRequest.objects.filter(requester=request.user).select_related("assigned_donor__user").order_by("-created_at")
    return render(request, "user_dashboard/my_requests.html", {"requests": requests})




@user_required
def donor_requests(request):
    profile = _get_profile(request.user)

    if not profile:
        messages.warning(
            request,
            "Complete your donor profile first."
        )
        return redirect("user_dashboard:profile")

    # Requests where admin has specifically assigned this donor
    requests = BloodRequest.objects.filter(
        assigned_donor=profile,
        status="Approved",
    ).select_related(
        "requester"
    ).order_by("-created_at")

    return render(
        request,
        "user_dashboard/donor_requests.html",
        {
            "requests": requests,
            "profile": profile,
        }
    )



@user_required
def donor_request_action(request, pk):

    if request.method != "POST":
        return redirect("user_dashboard:donor_requests")

    profile = _get_profile(request.user)

    if not profile:
        messages.warning(
            request,
            "Complete your donor profile first."
        )
        return redirect("user_dashboard:profile")

    # Only the donor assigned by admin can respond
    blood_request = get_object_or_404(
        BloodRequest,
        pk=pk,
        assigned_donor=profile,
        status="Approved"
    )

    action = request.POST.get("action")

    # =========================
    # DECLINE
    # =========================
    if action == "decline":

        blood_request.assigned_donor = None
        blood_request.donor_response = "Declined"
        blood_request.donor_responded_at = timezone.now()

        blood_request.save(
            update_fields=[
                "assigned_donor",
                "donor_response",
                "donor_responded_at",
            ]
        )

        # Notify receiver
        Notification.objects.create(
            user=blood_request.requester,
            message=(
                f"The assigned donor declined your "
                f"{blood_request.blood_group} blood request. "
                f"The administrator will look for another donor."
            )
        )

        messages.info(
            request,
            "You declined this blood request."
        )

        return redirect(
            "user_dashboard:donor_requests"
        )

    # =========================
    # ACCEPT
    # =========================
    if action == "accept":

        date_text = request.POST.get(
            "donation_date",
            ""
        ).strip()

        time_text = request.POST.get(
            "donation_time",
            ""
        ).strip()

        if not date_text or not time_text:
            messages.error(
                request,
                "Please select donation date and time."
            )
            return redirect(
                "user_dashboard:donor_requests"
            )

        from datetime import date, datetime

        try:
            donation_date = date.fromisoformat(
                date_text
            )

            donation_time = datetime.strptime(
                time_text,
                "%H:%M"
            ).time()

        except ValueError:
            messages.error(
                request,
                "Invalid donation date or time."
            )
            return redirect(
                "user_dashboard:donor_requests"
            )

        # Date cannot be in past
        if donation_date < timezone.localdate():
            messages.error(
                request,
                "Donation date cannot be in the past."
            )
            return redirect(
                "user_dashboard:donor_requests"
            )

        # Check same donor/date/time conflict
        conflict = Donation.objects.filter(
            donor=profile,
            donation_date=donation_date,
            donation_time=donation_time,
            status="Scheduled"
        ).exists()

        if conflict:
            messages.error(
                request,
                "You already have a scheduled donation at this date and time."
            )
            return redirect(
                "user_dashboard:donor_requests"
            )

        # Create donation
        donation = Donation.objects.create(
            donor=profile,
            request=blood_request,
            hospital=blood_request.hospital_name,
            blood_group=blood_request.blood_group,
            donation_date=donation_date,
            donation_time=donation_time,
            status="Scheduled",
        )

        # Update blood request
        blood_request.donor_response = "Accepted"
        blood_request.donor_responded_at = timezone.now()

        blood_request.save(
            update_fields=[
                "donor_response",
                "donor_responded_at",
            ]
        )

        # Donor becomes unavailable
        profile.available_to_donate = False
        profile.save(
            update_fields=[
                "available_to_donate"
            ]
        )

        # Notify receiver
        Notification.objects.create(
            user=blood_request.requester,
            message=(
                f"A donor accepted your "
                f"{blood_request.blood_group} blood request. "
                f"Donation is scheduled for "
                f"{donation_date:%d %b %Y} at "
                f"{donation_time:%H:%M} at "
                f"{blood_request.hospital_name}."
            )
        )

        # Notify donor
        Notification.objects.create(
            user=profile.user,
            message=(
                f"Your donation is scheduled for "
                f"{donation_date:%d %b %Y} at "
                f"{donation_time:%H:%M} at "
                f"{blood_request.hospital_name}."
            )
        )

        messages.success(
            request,
            "Request accepted and donation scheduled successfully."
        )

        return redirect(
            "user_dashboard:donor_requests"
        )

    messages.error(
        request,
        "Invalid action."
    )

    return redirect(
        "user_dashboard:donor_requests"
    )




@user_required
def donation_history(request):
    profile = _get_profile(request.user)
    donations = Donation.objects.filter(donor=profile).select_related("request__requester").order_by("-donation_date", "-created_at") if profile else Donation.objects.none()
    return render(request, "user_dashboard/donation_history.html", {"donations": donations, "profile": profile})


@user_required
def notifications(request):
    items = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "user_dashboard/notification.html", {"notifications": items})


@user_required
def mark_notification_read(request, pk):
    if request.method != "POST":
        return redirect("user_dashboard:notifications")
    item = get_object_or_404(Notification, pk=pk, user=request.user)
    item.is_read = True
    item.save(update_fields=["is_read"])
    return redirect("user_dashboard:notifications")


@user_required
def faq(request):
    faqs = [
        ("How often can I donate blood?", "Most eligible whole-blood donors can donate about every 56 days, subject to local medical guidance."),
        ("What should I do before donating?", "Eat a normal meal, drink enough water, and follow the instructions of the donation center."),
        ("How do I request blood?", "Open Request Blood, complete the patient and hospital details, and submit the request for admin approval."),
        ("How do donor requests work?", "After admin approval, matching available donors receive the request. A donor can accept with a date and time or decline it."),
        ("How will I know if my request is approved?", "The status is visible in My Requests and a notification is created when an admin reviews it."),
        ("Can I change my donor availability?", "Yes. Open My Profile and turn Available to Donate on or off."),
    ]
    return render(request, "user_dashboard/faq.html", {"faqs": faqs})


@user_required
def statistics(request):
    profile = _get_profile(request.user)
    my_donations = Donation.objects.filter(donor=profile) if profile else Donation.objects.none()
    my_requests = BloodRequest.objects.filter(requester=request.user)
    context = {
        "profile": profile,
        "total_donations": my_donations.count(),
        "completed_donations": my_donations.filter(status="Completed").count(),
        "scheduled_donations": my_donations.filter(status="Scheduled").count(),
        "total_requests": my_requests.count(),
        "pending_requests": my_requests.filter(status="Pending").count(),
        "approved_requests": my_requests.filter(status="Approved").count(),
        "rejected_requests": my_requests.filter(status="Rejected").count(),
        "completed_requests": my_requests.filter(status="Completed").count(),
    }
    return render(request, "user_dashboard/statistics.html", context)
