from django.urls import path
from . import views

urlpatterns = [
    path('studioAdd/', views.studioAdd, name='studioAdd'),
    path('studioUpdate/', views.studioUpdate, name='studioUpdate'),
    path('workshopAdd/', views.workshopAdd, name='workshopAdd'),
    path('workshopUpdate/', views.workshopUpdate, name='workshopUpdate'),
    path('freeTrialBookings/', views.freeTrialBookings, name='freeTrialBookings'),
    path('sendEmail/', views.sendEmail, name='sendEmail'),
]
