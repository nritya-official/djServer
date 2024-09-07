from django.urls import path
from .views import *
urlpatterns = [ 
    path('studioEntityBookingsReport/', studioEntityBookingsReport, name='studioEntityBookingsReport'),
]