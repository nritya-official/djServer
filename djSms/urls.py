from django.urls import path
from .views import *

urlpatterns = [
    path('request_otp/', request_otp, name='request_otp'),
    path('confirm_otp/', confirm_otp, name='confirm_otp'),
]
