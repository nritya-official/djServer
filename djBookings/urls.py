# bookings/urls.py
from django.urls import path
from .views import bookingsTest, freeTrial
urlpatterns = [
    path('testEndpoint/', bookingsTest, name='bookingsTest'),
    path('freeTrial/', freeTrial, name='freeTrial'),
    # Add more paths as needed
]
