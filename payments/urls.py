from django.urls import path
from .views import create_payment, verify_payment, intitate_booking, testEndpoint

urlpatterns = [
    path('', testEndpoint, name='testEndpoint'),
    path('razorpay_order', create_payment, name='razorpay_order'),
    path('razorpay_callback', verify_payment, name='razorpay_callback'),
    path( 'intitate_booking', intitate_booking, name='intitate_booking'),
]
