from django.urls import path
from .views import create_payment, verify_payment

urlpatterns = [
    path('razorpay_order', create_payment, name='razorpay_order'),
    path('razorpay_callback', verify_payment, name='razorpay_callback'),
]
