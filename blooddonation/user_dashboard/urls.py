from django.urls import path
from . import views

app_name = "user_dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("search-donors/", views.search_donors, name="search_donors"),
    path("request-blood/", views.request_blood, name="request_blood"),

    # path('request-blood/<int:donor_id>/', views.request_blood, name='request_blood'),
    path("my-requests/", views.my_requests, name="my_requests"),
    path("donor-requests/", views.donor_requests, name="donor_requests"),
    path("donor-requests/<int:pk>/action/", views.donor_request_action, name="donor_request_action"),
    # path("blood-request/<int:pk>/accept/",views.accept_blood_request, name="accept_blood_request"),
    # path("blood-request/<int:pk>/decline/",views.decline_blood_request,name="decline_blood_request"),
    path("donations/", views.donation_history, name="donation_history"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("faq/", views.faq, name="faq"),
    path("statistics/", views.statistics, name="statistics"),
]
