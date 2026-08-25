# from django.urls import path
# from . import views

# urlpatterns = [

#     path("",views.admin_dashboard,name="admin_dashboard"),

#     path("donors/",views.manage_donors,name="manage_donors"),

#     path("requests/",views.blood_requests,name="blood_requests"),

#     path("approved-requests/",views.approved_requests,name="approved_requests"),

#     path("users/",views.manage_users,name="manage_users"),

#     path("reports/",views.reports,name="reports"),
# ]


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
    path("approved-requests/", views.approved_requests, name="approved_requests"),

    #Users
    path("users/", views.users, name="users"),
    path("users/<int:pk>/toggle/", views.toggle_user, name="toggle_user"),

    #Reports
    path("reports/", views.reports, name="reports"),
]