from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    #Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    #Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    #Donors
    path("donors/", views.donors, name="donors"),
    path("donors/<int:pk>/", views.donor_detail, name="donor_detail"),

    #Blood requests
    path("requests/", views.requests_page, name="requests"),
    path("requests/<int:pk>/approve/", views.approve_request, name="approve_request"),
    path("requests/<int:pk>/reject/", views.reject_request, name="reject_request"),
    path("requests/<int:pk>/assign-donor/", views.assign_donor,name="assign_donor"),
    path("approved-requests/", views.approved_requests, name="approved_requests"),

    #Users
    path("users/", views.users, name="users"),
    path("users/<int:pk>/toggle/", views.toggle_user, name="toggle_user"),

    #Reports
    path("reports/", views.reports, name="reports"),


    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/read-all/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path("donations/", views.donations, name="donations"),
    path("donations/<int:pk>/complete/", views.complete_donation, name="complete_donation"),
]