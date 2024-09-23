# bookings/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('testEndpoint/', bookingsTest, name='bookingsTest'),
    path('freeTrial/', freeTrial, name='freeTrial'),
    path('bookEntity/', bookEntity, name='bookEntity'),
    path('availFreeTrial/<str:booking_id>', availFreeTrial, name='availFreeTrial'),
    path('availFreeTrialResults/', availFreeTrialResults, name='availFreeTrialResults'),
    path('getUserBookings/<str:user_id>', getUserBookings, name='getUserBookings'),
    # Add more paths as needed availFreeTrialResults
]
