from django.urls import path
from .views import *
urlpatterns = [ 
    path('', testEndpoint, name='testEndpoint'),
    path('studioEntityBookingsReport/', studioEntityBookingsReport, name='studioEntityBookingsReport'),
    path('getAllOwnerStudio/', getAllOwnerStudio, name='getAllOwnerStudio'),
]