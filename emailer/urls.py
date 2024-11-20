from django.urls import path
from .views import *

urlpatterns = [
    path('', testEndpoint, name='testEndpoint'),
    path('studioAdd/', StudioAdd.as_view(), name='studioAdd'),
    path('studioUpdate/', StudioUpdate.as_view(), name='studioUpdate'),
    path('workshopAdd/', WorkshopAdd.as_view(), name='workshopAdd'),
    path('workshopUpdate/', WorkshopUpdate.as_view(), name='workshopUpdate'),
    path('freeTrialBookings/', FreeTrialBookings.as_view(), name='freeTrialBookings'),
    path('sendEmail/', SendEmail.as_view(), name='sendEmail'),
]
