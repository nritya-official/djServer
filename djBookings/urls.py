# bookings/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('testEndpoint/', bookingsTest, name='bookingsTest'),
    path('bookSlot/', bookSlot, name='bookSlot'),
    path('freeTrial/', freeTrial, name='freeTrial'),
    path('availFreeTrial/<str:booking_id>', availFreeTrial, name='availFreeTrial'),
    path('availFreeTrialResults/', availFreeTrialResults, name='availFreeTrialResults'),
    path('getUserBookings/', getUserBookings, name='getUserBookings'),
    # Add more paths as needed availFreeTrialResults
]
