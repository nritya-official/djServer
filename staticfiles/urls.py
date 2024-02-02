# bookings/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('testEndpoint/', bookingsTest, name='bookingsTest'),
    path('freeTrial/', freeTrial, name='freeTrial'),
    path('availFreeTrial/<str:booking_id>', availFreeTrial, name='availFreeTrial'),
    # Add more paths as needed
]
