from django.urls import path
from . import views

urlpatterns = [

    path('', views.home,name='home'),
    path('index/', views.home),
    path('about/', views.about,name='about'),
    path('contact/', views.contact,name='contact'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('doner/', views.search_donor, name='doner'),
    path('request-blood/', views.blood_request_view, name='request_blood'),
    path('blood-requests/', views.request_list_view, name='request_list'),
    path('become-a-donor/', views.become_a_donor, name='become_a_donor'),

]
